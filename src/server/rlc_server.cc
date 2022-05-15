
#include <iostream>
#include <memory>
#include <string>

// grpc related Imports
#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

#include "../cmake/build/observation_action.grpc.pb.h"

// godot shared memory interface import
#include "../godotInterface/cGodotSharedInterface.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReader;
using grpc::ServerReaderWriter;
using grpc::ServerWriter;
using grpc::Status;

using rlc::RLC;
using rlc::ObservationData;
using rlc::ActionData;
using rlc::Empty;

// server logics
class RCServiceImpl final : public RLC::Service {

    
    // make a cSharedMemoryTensor
    cSharedMemoryTensor mem = cSharedMemoryTensor("env");
    // make the necessary sempahores to sync the reads and writes
    cSharedMemorySemaphore sem_obs = cSharedMemorySemaphore("obs_semaphore", 0);
    cSharedMemorySemaphore sem_act = cSharedMemorySemaphore("act_semaphore", 0);

    // create new tensors in the shared memory space; so the server can communicate with godot
    //cPersistentIntTensor *actionTensor = mem.newIntTensor("action", 1);
    // vector that holds the agent action(s)
    cPersistentFloatTensor *actionTensor;// = mem.newFloatTensor("action", 2);;
    // vector that holds the simulation control actions (reset and terminate)
    cPersistentIntTensor *envActionTensor = mem.newIntTensor("env_action", 2);
    // vector to read the observations from godot
    cPersistentFloatTensor *observationTensor;// = mem.newFloatTensor("observation", 21);
    // reward vector (index the 0 for scalar rewards)
    cPersistentFloatTensor *rewardTensor = mem.newFloatTensor("reward", 1);
    // done vector (index 0 for the done scalar (0 when not done, 1 when done))
    cPersistentIntTensor *doneTensor = mem.newIntTensor("done", 1);

    // grpc procedure to step the environment, client send a action with the request,
    // server response the package of observation info (observations, reward, done) to the client to process
    Status Step(ServerContext *context, 
                     const ActionData *request, 
                     ObservationData *reply) override {

        // https://www.programmersought.com/article/84463145457/

        
        // vectors to hold simulation control parameters, actions, reward, done and observations; 
        // we receive it from the client and write to the godot-grpc shared memory space
        std::vector<int64_t> env_action_vec;
        std::vector<float> observations, action_vec;
        float reward;
        int64_t is_done;
        //std::cout << "Stepping" << std::endl;

        // collect the actions received from the client
        for (int i = 0; i < request->action_index_size(); i++) {
            //std::cout << request->action_index(i) << std::endl;
            //float action_received = float(request->action_index(i));
            action_vec.push_back(request->action_index(i));
        }
        
        // write to the shared memory so the godot can use the actions make new observations
        actionTensor->write(action_vec);
        // collect the simulation control parameter (reset in this case) and write to godot
        env_action_vec.push_back(request->env_action());
        envActionTensor->write(env_action_vec);
        // release (increment the count) the semaphore
        // so the godot can process the action
        sem_act.post();

        // hold (decrement the count) the semaphore and receive the observations from godot
        sem_obs.wait();
        observations = observationTensor->read(); // read the observations from the shared memory space
        reward = rewardTensor->read()[0]; // read the reward from the shared memory space
        is_done = doneTensor->read()[0]; // read the done from the shared memory space
        
        // send the observation response
        reply->set_is_done(is_done); // done response
        for(int i = 0; i < observations.size(); ++i) {
            reply->add_observations(observations[i]); // observation vector response
        }
        reply->set_reward(reward); // reward response
        
        // Procedure success status
        return Status::OK;
    }

    // grpc procedure to reset the environment.
    Status Reset(ServerContext *context,
                const Empty *request,
                ObservationData *reply) override {
        
        // vectors to hold the initial observation infos
        std::vector<float> observations;
        float reward;
        int64_t is_done;
        
        // initialise vector with reset true (1) and terminate false (0)
        std::vector<int64_t> reset = {1, 0};
        // write the environment control parameters to godot
        envActionTensor->write(reset);
        // release the semaphore
        sem_act.post();

        // hold the semaphore
        sem_obs.wait();
        // read the observation infos (initial) from godot
        observations = observationTensor->read();
        reward = rewardTensor->read()[0];
        is_done = doneTensor->read()[0];

        // send the initial observation infos to the client
        reply->set_is_done(is_done);

        for(int i = 0; i < observations.size(); ++i) {
            reply->add_observations(observations[i]);
        }
        reply->set_reward(reward);
        // Procedure success status
        return Status::OK;
    }

    // grpc procedure that terminates the godot environment
    Status Terminate(ServerContext *context,
                const Empty *request,
                Empty *reply) override {
        // set the simulation control parameters to terminate
        std::vector<int64_t> terminate = {0, 1};
        // write the parameters to the shared memory
        envActionTensor->write(terminate);
        // release the semaphore and terminate the simulation
        sem_act.post();

        // explicit destruction of the objects to free the memory
        envActionTensor->~cPersistentIntTensor();
        doneTensor->~cPersistentIntTensor();
        actionTensor->~cPersistentFloatTensor();
        observationTensor->~cPersistentFloatTensor();
        rewardTensor->~cPersistentFloatTensor();

        // server response status
        return Status::OK;

    }

    public:
        int num_actions;
        int num_observations;

        RCServiceImpl(int number_of_actions, int number_of_observations) {
            num_actions = number_of_actions;
            num_observations = number_of_observations;

            actionTensor = mem.newFloatTensor("action", num_actions);
            observationTensor = mem.newFloatTensor("observation", num_observations);
        };

};

// run the server
void RunServer(int number_of_actions, int number_of_observations) {
    std::string server_address("0.0.0.0:50051");
    //int number_of_actions = 2;
    //int number_of_observations = 21;
    
    RCServiceImpl service(number_of_actions, number_of_observations);

    //grpc::EnableDefaultHealthCheckService(true);
    //grpc::reflection::InitProtoReflectionServerBuilderPlugin();
    // server builder
    ServerBuilder builder;
    // listen to the given address
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // finally assemble the server
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on: " << server_address << std::endl;
    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();

}

int main(int argc, char** argv) {
    if (argc == 3) {
        int number_of_actions = std::stoi(argv[1]);
        int number_of_observations = std::stoi(argv[2]);

        RunServer(number_of_actions, number_of_observations);
    }
    else {
        std::cout << "Please provide the number of actions, then number of observations" << std::endl;
    }

    return 0;
}
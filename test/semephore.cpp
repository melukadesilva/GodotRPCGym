#include <boost/interprocess/sync/named_semaphore.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>

#include <cstdlib> //std::system
#include <sstream>
#include <iostream>
#include <vector>

#include <unistd.h>
#include <fstream>

#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost/interprocess/sync/interprocess_semaphore.hpp>
#include <boost/exception/all.hpp>

using namespace boost::interprocess;


typedef allocator<int, managed_shared_memory::segment_manager>  ShmemAllocator;
typedef std::vector<int, ShmemAllocator> IntVector;
typedef std::vector<float, ShmemAllocator> FloatVector;

class cSharedMemorySemaphore {
private:
    std::string *name;
    mapped_region *region;
    boost::interprocess::interprocess_semaphore *mutex;

public:
    cSharedMemorySemaphore(){;};
    ~cSharedMemorySemaphore(){
        shared_memory_object::remove(name->c_str());
        delete region;
        delete name;
    };
    void init(const std::string &sem_name){

        name = new std::string(sem_name);
        std::cout<<"Constructing semaphore "<<name<<std::endl;
        try{
            shared_memory_object object(open_only, name->c_str(), read_write);
            region = new mapped_region(object, read_write);
        }catch(boost::interprocess::interprocess_exception &e){
            std::cout<<boost::diagnostic_information(e)<<std::endl;
            shared_memory_object::remove(name->c_str());
        }
        std::cout<<"Constructed semaphore "<<name<<std::endl;
    };
    void post(){
        std::cout<<"Post semaphore "<<name<<std::endl;
        mutex = static_cast<interprocess_semaphore*>(region->get_address());
        mutex->post();
    };
    void wait(){
        std::cout<<"Wait semaphore "<<name<<std::endl;
        mutex = static_cast<interprocess_semaphore*>(region->get_address());
        mutex->wait();
    };
};

int main (int argc, char *argv[])
{
    const char *semaphore_name;
    const char *segment_name;
    const char *read_handle;

    if(argc<2){
        std::cout<<"Segment name not found"<<std::endl;
        return -1;
    }else{
        semaphore_name = argv[1];
        segment_name = argv[2];
        read_handle = argv[3];
    }
    std::cout<<"Semaphore name = "<<semaphore_name<<std::endl;
    std::cout<<"Segment name = "<<segment_name<<std::endl;

    try {
        cSharedMemorySemaphore sem;
        sem.init(semaphore_name);
        // open the shared memory
        managed_shared_memory segment(open_only, segment_name);

        for(int i = 0; i < 2; i++){
            // sem.wait();
            FloatVector *v = segment.find<FloatVector> (read_handle).first;
            std::cout<<"C++ from Python = [";
            for(int i=0;i<v->size(); i++){
                std::cout<<(*v)[i]<<", ";
            }
            std::cout<<"]";
            // segment.destroy<FloatVector>(read_handle);
            sem.post();
        }

        return 0;
    } catch (interprocess_exception& e) {
        std::cout << e.what( ) << std::endl;
        return 1;
    }
}
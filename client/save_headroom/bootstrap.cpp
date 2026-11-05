#define PROSPERO_ZIP_OPEN_BUDGET "8"
#define PROSPERO_FINAL_SDL_EXIT 1
#define PROSPERO_MANAGEMENT_EXT 1
#define PROSPERO_STARTUP_OBSERVER "false"
#define PROSPERO_PREPARE_ZINK_SCREEN 1
#define PROSPERO_CLEAN_SYSTEM_EXIT 1
/* Candidate-only upstream synchronous flush/context policy; clean-exit gate retained. */
#include "../launcher/storage_paths.hpp"
#define ps5shaderc_fault_begin prospero_storage_fault_begin
#define ps5shaderc_fault_end prospero_storage_fault_end
#define ps5shaderc_fault_status prospero_storage_fault_status
#define ps5shaderc_fault_extended_status prospero_storage_fault_extended_status
#define main prospero_zink_main
#include "../startup/bootstrap.cpp"
#undef main
#include "../ports/zink/submit_policy.hpp"
int main(int argc,char** argv){
 if(!prospero_storage::initialize())return 1;
 if(setenv("PROSPERO_GLFW_FINAL_SDL_QUIT","1",1)!=0)return 1;
 int rc=prospero_zink::enable_flushsync();
 if(rc){std::fprintf(stderr,"PS5_ZINK flushsync setup failed result=%d\n",rc);return 1;}
 rc=prospero_zink::enable_synchronous_context();
 if(rc){std::fprintf(stderr,"PS5_ZINK direct context setup failed result=%d\n",rc);return 1;}
 return prospero_zink_main(argc,argv);
}

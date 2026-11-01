#define PROSPERO_CLEAN_SYSTEM_EXIT 1
/* Candidate-only upstream synchronous flush policy; normal startup/quit retained. */
#define main prospero_zink_main
#include "../startup/bootstrap.cpp"
#undef main
#include "../ports/zink/submit_policy.hpp"
int main(int argc,char** argv){
 int rc=prospero_zink::enable_flushsync();
 if(rc){std::fprintf(stderr,"PS5_ZINK flushsync setup failed result=%d\n",rc);return 1;}
 return prospero_zink_main(argc,argv);
}

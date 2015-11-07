/* testOpenMP.c */
#include <omp.h>
#include "mex.h"
void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[] )
{
	int nthreads, tid;
	//omp_set_num_threads(4);
	mexPrintf("Number of processors: %d\n", omp_get_num_procs());
	#pragma omp parallel private(nthreads, tid) 
	{
		tid = omp_get_thread_num();
		mexPrintf("Hello World from thread = %d\n", omp_get_thread_num() );
	}
}
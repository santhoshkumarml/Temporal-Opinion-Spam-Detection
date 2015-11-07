// PSGD_Yahoo.cpp : Defines the entry point for the console application.
//

//#include "stdafx.h"

/*--------------Usage: mex_PSGD_Yahoo(X, y, eta, lambda, detail)---------------*/

#include "mex.h"
#include <iostream>
#include <omp.h>
#include <fstream>
#include <cmath>
#include <time.h>
#include <cstdlib>
#include <memory>

using namespace std;


double ** X;
double * y;
double * w;
double eta, lambda;

int N, D;
int method; //0: sequential stochSubGD; 1: parallel stochSubGD.
int detail; //0: no output; 1: output details.

char * X_file;
char * y_file;

/* returns a random permutation of the numbers {1,2,...,n} */
int* random_permutation(int n) {
	
	int *p = new int [n];
	for (int i = 0; i < n; i++) {
		int j = rand() % (i + 1);
		p[i] = p[j];
		p[j] = i;
	}
	return p;
}

void shuffle_Xy(int start, int end)
{
	int len = end-start+1;
	double ** cpy_X = new double * [len];
	for(int i = 0; i < len; i++){
		cpy_X[i] = X[start+i];
	}
	
	int * rand_perm = random_permutation(len);
	for(int i = 0; i < len; i++){
		X[start+i] = cpy_X[rand_perm[i]];
	}

	double * cpy_y = new double [len];
	for(int i = 0; i < len; i++){
		cpy_y[i] = y[i];
	}

	for(int i = 0; i < len; i++){
		y[i] = cpy_y[rand_perm[i]];
	}
	
	delete [] cpy_X;
	delete [] cpy_y;
}

double inner_prod(double * a, double * b, int dim)
{
	double prod = 0;
	for(int i = 0; i < dim; i++){
		prod += a[i]*b[i];
	}
	return prod;
}

double get_obj()
{
	double obj = 0;
	for(int i = 0; i < N; i++){
		obj += pow(inner_prod(X[i], w, D) - y[i], 2.0);
	}
	for(int i = 0; i < D; i++){
		obj += lambda * abs(w[i]);
	}
	return obj;
}

void PSGD()
{
	double ** tot_w;
	int tid;
	int n_threads;
	/* get total number of threads */
#pragma omp parallel private(tid)
	{
		tid = omp_get_thread_num();
		if(tid == 0){
			n_threads = omp_get_num_threads();
			//cout<<"Number of threads = "<<n_threads<<endl;
			if(detail == 1){
				mexPrintf("Number of threads = %d\n", n_threads);
			}
		}
	}


	w = new double [D];
	for(int i = 0; i < D; i++){
		w[i] = 0;
	}
	double obj = get_obj();
	//cout<<"Initial object function = "<<obj<<endl;
	if(detail == 1){
		mexPrintf("Initial object function = %f\n", obj);
	}

	tot_w = new double *[n_threads];
	for(int i = 0; i < n_threads; i++){
		tot_w[i] = new double [D];
	}
	for(int i = 0; i < n_threads; i++){
		for(int j = 0; j < D; j++){
			tot_w[i][j] = 0;
		}
	}

	/* each core sequentially update w on its own partition */
#pragma omp parallel private(tid)
	{
		int start, end;
		int partition_len = (int)floor((double)N/n_threads);

		tid = omp_get_thread_num();
		if(tid == n_threads-1){
			start = (n_threads-1)*partition_len;
			end = N-1;
		} else {
			start = tid*partition_len;
			end = start + partition_len - 1;
		}

		//cout<<"tid="<<tid<<", start="<<start<<", end="<<end<<endl;
		
		for(int n = start; n <= end; n++)
		{
			double * delta_w = new double [D];
			double resid = inner_prod(X[n], tot_w[tid], D) - y[n];

			for(int i = 0; i < D; i++){
				delta_w[i] = resid * X[n][i];
				if(tot_w[tid][i] > 0){
					delta_w[i] += lambda;
				} else if(tot_w[tid][i] < 0){
					delta_w[i] -= lambda;
				}
			}

			for(int i = 0; i < D; i++){
				tot_w[tid][i] = tot_w[tid][i] - eta * delta_w[i];
			}
			
			delete [] delta_w;
		}
	}

	/* aggregate all w from each core */
	for(int i = 0; i < D; i++){
		w[i] = 0;
		for(int j = 0; j < n_threads; j++){
			w[i] += tot_w[j][i];
		}
		w[i] /= (double)n_threads;
	}
	obj = get_obj();
	//cout<<"Object function = "<<obj<<endl;
	
	for(int i = 0; i < n_threads; i++){
		delete tot_w[i];
	}
	delete [] tot_w;
}


void read_data()
{
	ifstream fin_X(X_file);
	ifstream fin_y(y_file);

	fin_X>>N>>D;
	X = new double * [N];
	for(int i = 0; i < N; i++){
		X[i] = new double [D];
	}
	y = new double [N];

	for(int i = 0; i < N; i++){
		for(int j = 0; j < D; j++){
			fin_X>>X[i][j];
		}
	}
	for(int i = 0; i < N; i++){
		fin_y>>y[i];
	}
}

int main(int argc, char* argv[])
{
	X_file = "toy_X.txt";
	y_file = "toy_y.txt";

	/* read N, D, X, y from file */
	read_data();

	/* set parameters */
	lambda = 1;
	eta = 0.01;
	
	srand(time(NULL));
	shuffle_Xy(0, N-1);

	PSGD();

	/*
	for(int i = 0; i < D; i++){
		cout<<w[i]<<" ";
	}
	cout<<endl;*/

	return 0;
}

void mexFunction(int nlhs, mxArray *plhs[ ], int nrhs, const mxArray *prhs[ ]) {
	/* get X (design matrix) */
	N = (int)mxGetM(prhs[0]);
    D = (int)mxGetN(prhs[0]);
	
    X = new double*[N];
    for (int i = 0; i < N; i++){ X[i] = new double[D]; }
    
    double *ptr = (double *)mxGetPr(prhs[0]);
    for (int i = 0; i < D; i++){
        for (int j = 0; j < N; j++){
            X[j][i] = ptr[i*N + j];
        }
    }
    
	/* get y (labels) */
	y = new double[N];
    ptr = (double *)mxGetPr(prhs[1]);
    for (int i = 0; i < N; i++){
        y[i] = ptr[i];
    }
	
	/* get eta, lambda, detail */
	eta = *((double *)mxGetPr(prhs[2]));
	lambda = *((double *)mxGetPr(prhs[3]));
	detail = (int) *((double *)mxGetPr(prhs[4]));
	
	if(detail == 1){
		mexPrintf("N=%d, D=%d, lambda%f\n", N, D, lambda);
	}
	
	/* run method */
	long start_time = omp_get_wtime();
	srand(time(NULL));
	shuffle_Xy(0, N-1);

	PSGD();
	
	if(detail == 1){
		double obj = get_obj();
		long time = omp_get_wtime() - start_time;
		mexPrintf("Final object function = %f, time= %lu\n", obj, time);
	}
	
	
		
	/* create return value */
	double *output;
    plhs[0] = mxCreateDoubleMatrix(D, 1, mxREAL);
    output = mxGetPr(plhs[0]);
    
    for(int i = 0; i < D; i++)
        output[i] = w[i];
	
	/* clear memory */
	for(int i = 0; i < N; i++)
		delete [] X[i];
	delete [] X;
	
	delete [] y;
	
	delete [] w;
	
}

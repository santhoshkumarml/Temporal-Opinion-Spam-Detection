// PStocSubGD.cpp : Defines the entry point for the console application.
//

//#include "stdafx.h"

/*--------------Usage: mex_PStocSubGD(X, y, eta, lambda, maxIter, method, detail)---------------*/
/*method: 0 for sequential stochSubGD; 1 for parallel stochSubGD. */

#include "mex.h"
#include <iostream>
#include <omp.h>
#include <fstream>
#include <cmath>
#include <time.h>

using namespace std;


double ** X;
double * y;
double * w;
double eta, lambda;

int N, D;
int maxIter;
int method; //0: sequential stochSubGD; 1: parallel stochSubGD.
int detail; //0: no output; 1: output details.

char * X_file;
char * y_file;

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

void par_stocSubGD()
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
	tot_w = new double * [n_threads];
	for(int i = 0; i < n_threads; i++){
		tot_w[i] = new double [D];
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

	/* main loop */
	for(int iter = 0; iter < maxIter; iter++){

		/* each core uniformly pick one data point and update w*/
#pragma omp parallel private(tid)
		{
			tid = omp_get_thread_num();
			srand(tid+iter);
			int rand_n = ((int)rand()) % N;
			//cout<<"tid="<<tid<<", rand_n="<<rand_n<<endl;
			double * delta_w = new double [D];
			double resid = inner_prod(X[rand_n], w, D) - y[rand_n];

			for(int i = 0; i < D; i++){
				delta_w[i] = resid * X[rand_n][i];
				if(w[i] > 0){
					delta_w[i] += lambda;
				} else if(w[i] < 0){
					delta_w[i] -= lambda;
				}
			}

			for(int i = 0; i < D; i++){
				tot_w[tid][i] = w[i] - eta * delta_w[i];
			}
			
			delete [] delta_w;
		}

		/* aggregate all w from each core */
		for(int i = 0; i < D; i++){
			w[i] = 0;
			for(int j = 0; j < n_threads; j++){
				w[i] += tot_w[j][i];
			}
			w[i] /= (double)n_threads;
		}
		double obj = get_obj();
		//cout<<"Iteration "<<iter<<", object function = "<<obj<<endl;
		if(detail == 1){
			mexPrintf("Iteration %d, object function = %f\n", iter, obj);
		}
	}
	for(int i = 0; i < n_threads; i++){
		delete [] tot_w[i];
	}
	delete [] tot_w;
}

void stocSubGD()
{
	w = new double [D];
	for(int i = 0; i < D; i++){
		w[i] = 0;
	}
	double obj = get_obj();
	//cout<<"Initial object function = "<<obj<<endl;
	if(detail == 1){
		mexPrintf("Initial object function = %f\n", obj);
	}

	/* main loop */
	for(int iter = 0; iter < maxIter; iter++){

		/* each time uniformly pick one data point and update w*/

		int rand_n = ((int)rand()) % N;
		double * delta_w = new double [D];
		double resid = inner_prod(X[rand_n], w, D) - y[rand_n];

		for(int i = 0; i < D; i++){
			delta_w[i] = resid * X[rand_n][i];
			if(w[i] > 0){
				delta_w[i] += lambda;
			} else if(w[i] < 0){
				delta_w[i] -= lambda;
			}
		}

		for(int i = 0; i < D; i++){
			w[i] = w[i] - eta * delta_w[i];
		}

		double obj = get_obj();
		//cout<<"Iteration "<<iter<<", object function = "<<obj<<endl;
		if(detail == 1){
			long time = clock();
			mexPrintf("Iteration %d, clock= %lu object function = %f\n", iter,time, obj);
		}
		
		delete [] delta_w;
	}
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
	maxIter = 1000;
	method = 1;
	
	/* run method */
	if(method == 0){
		stocSubGD();
	} else if(method == 1){
		par_stocSubGD();
	} else {
		//cout<<"Method: 0 for sequential stocSubGD, 1 for parallel stocSubGD"<<endl;
		mexPrintf("Method: 0 for sequential stocSubGD, 1 for parallel stocSubGD\n");
	}

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
	
	/* get eta, lambda, maxIter, method */
	eta = *((double *)mxGetPr(prhs[2]));
	lambda = *((double *)mxGetPr(prhs[3]));
	maxIter = (int) *((double *)mxGetPr(prhs[4]));
	method = (int) *((double *)mxGetPr(prhs[5]));
	detail = (int) *((double *)mxGetPr(prhs[6]));
	
	if(detail == 1){
		mexPrintf("N=%d, D=%d, method=%d, maxIter=%d\n", N, D, method, maxIter);
	}
	
	/* run method */
	srand(time(NULL));
	if(method == 0){
		stocSubGD();
	} else if(method == 1){
		par_stocSubGD();
	} else {
		mexPrintf("Method: 0 for sequential stocSubGD, 1 for parallel stocSubGD\n");
	}
	
	if(detail == 1){
		double obj = get_obj();
		mexPrintf("Final object function = %f\n", obj);
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


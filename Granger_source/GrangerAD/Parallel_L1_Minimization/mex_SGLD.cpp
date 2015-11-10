// SGLD.cpp : Defines the entry point for the console application.
//

//#include "stdafx.h"

/*--------Usage: mex_SGLD(X, y, a, b, gamma, lambda, batch_size, maxIter, detail)---------*/
/*eta = a*(b+t)^(-gamma) */

#include "mex.h"
#include <iostream>
#include <omp.h>
#include <fstream>
#include <cmath>
#include <time.h>
#include <random>
#include <stdlib.h>

using namespace std;

typedef std::tr1::ranlux64_base_01 Myeng; 

typedef std::tr1::normal_distribution<double> Gaussian_dist; 

double ** X;
double * y;
double * w;
double eta, lambda;
double a, b, gamma;

int N, D, batch_size;
int maxIter;
int detail;

char * X_file;
char * y_file;

double get_Gaussian(double mu, double sigma)
{
	Myeng eng; 
	eng.seed(100+rand());
	Gaussian_dist dist(mu, sigma);
	return dist(eng);
}

/* returns a random permutation of the numbers {1,2,...,n} */
int * random_permutation(int n) {
	
	int *p = new int [n];
	for (int i = 0; i < n; i++) {
		int j = rand() % (i + 1);
		p[i] = p[j];
		p[j] = i;
	}
	return p;
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

void SGLD()
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

		/* each time sample a bach of data points and update w using SGLD */

		// first 'batch_size' number of elements in 'rand_perm' serve as a batch.
		int * rand_perm = random_permutation(N);

		double * delta_w = new double [D];
		for(int i = 0; i < D; i++) delta_w[i] = 0;

		/* get delta_w*/
		for(int i = 0; i < batch_size; i++){
			int indx = rand_perm[i];
			double resid = inner_prod(X[indx], w, D) - y[indx];
			for(int j = 0; j < D; j++){
				delta_w[j] += 2*resid * X[indx][j];
			}
		}
		for(int i = 0; i < D; i++){
			delta_w[i] *= (double)N/batch_size;
			if(w[i] > 0){
				delta_w[i] += lambda;
			} else if(w[i] < 0){
				delta_w[i] -= lambda;
			}
		}

		eta = a*pow((double)(b+iter), (double)gamma);

		for(int i = 0; i < D; i++){
			w[i] = w[i] - 0.5 * eta * delta_w[i] - get_Gaussian(0, eta);
		}

		double obj = get_obj();
		//cout<<"Iteration "<<iter<<", object function = "<<obj<<endl;
		if(detail == 1){
			long time = clock();
			mexPrintf("Iteration %d, clock= %lu, object function = %f\n", iter, time, obj);
		}
		delete [] rand_perm;
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
	a = 0.000001;
	b = 100;
	gamma = 1;
	maxIter = 1000;
	batch_size = 2;
	
	/* run method */
	srand(time(0));
	SGLD();

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
	
	/* get a, b, gamma, lambda, batch_size, maxIter, detail */
	a = *((double *)mxGetPr(prhs[2]));
	b = *((double *)mxGetPr(prhs[3]));
	gamma = *((double *)mxGetPr(prhs[4]));
	lambda = *((double *)mxGetPr(prhs[5]));
	batch_size = (int) *((double *)mxGetPr(prhs[6]));
	maxIter = (int) *((double *)mxGetPr(prhs[7]));
	detail = (int) *((double *)mxGetPr(prhs[8]));
	
	
	if(detail == 1){
		mexPrintf("N=%d, D=%d, maxIter=%d\n", N, D, maxIter);
	}
	
	/* run method */
	srand(time(NULL));
	SGLD();
	
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


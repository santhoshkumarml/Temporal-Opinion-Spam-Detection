//  Copyright 2009 Shai Shalev-Shwartz, Ambuj Tewari

//  SCD version 2.1

/*
    This file is part of SCD.

    SCD is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SCD is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with SCD. If not, see <http://www.gnu.org/licenses/>.
*/
//#include "stdafx.h"

/*----------Usage: mex_SCD(X, y, lambda, loss_type, maxIter, detail)---------------  */
/* loss_type: 0 for logistic, 2 for squared (default = 0) */
#include "mex.h"
#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <sstream>
#include <ctime>
#include <string>

#include "cmd_line.h"
#include "Losses.h"

using namespace std;

class IndexValuePair {
public:
	IndexValuePair() { }
	IndexValuePair(uint i, double v) : first(i), second(v) { }

	uint first;
	double second;
};


// a sparse vector is just a vector of index, value pairs
typedef std::vector<IndexValuePair> sparse_vector;

void print_summary(std::vector<double>& innerprod_with_w,
		std::vector<double>& labels,
		std::vector<double>& w,
		int num_examples,
		double lambda,
		Losses& L) {

	double sum=0, mistakes=0;
	double w_norm = 0.0;
	uint w_density = 0;
	int j;

	for (j=-0; j<w.size(); j++) {
		double tmp = fabs(w[j]);
		w_norm += tmp;
		if (tmp > 0.0000001) w_density++;
	}

	for (j=0; j < num_examples; j++) {
		sum += L.loss(innerprod_with_w[j],labels[j]);
		if (labels[j] * (innerprod_with_w[j]) < 0) mistakes++;
	}
	
	sum /= num_examples;
	mistakes /= num_examples;

	/*
	std::cout << w_norm << " " << w_density << " "
		<< sum << " " << sum + lambda*w_norm
		<< " " << mistakes << std::endl;*/

}

double get_obj(std::vector<double>& innerprod_with_w,
		std::vector<double>& labels,
		std::vector<double>& w,
		int num_examples,
		double lambda,
		Losses& L) {

	double sum=0, mistakes=0;
	double w_norm = 0.0;
	uint w_density = 0;
	int j;

	for (j=-0; j<w.size(); j++) {
		double tmp = fabs(w[j]);
		w_norm += tmp;
		if (tmp > 0.0000001) w_density++;
	}

	for (j=0; j < num_examples; j++) {
		sum += L.loss(innerprod_with_w[j],labels[j]);
		if (labels[j] * (innerprod_with_w[j]) < 0) mistakes++;
	}
	sum *= 2;
	//sum /= num_examples;
	//mistakes /= num_examples;
	
	//mexPrintf("%f %f %f %f %d\n", w_norm, w_density, sum, sum+lambda*w_norm, mistakes);
	
	return sum + lambda*w_norm;
	/*
	std::cout << w_norm << " " << w_density << " "
		<< sum << " " << sum + lambda*w_norm
		<< " " << mistakes << std::endl;
	 */

}


void mexFunction(int nlhs, mxArray *plhs[ ], int nrhs, const mxArray *prhs[ ]) {
	// loss that the user wants to use
	int loss_type;

	// number of iterations for which to run SCD
	int num_iters;

	// print summary every so many iterations, 0 for no printing;
	int print_me;
	
	// regularization parameter
	double lambda;
	
		
	// choose seed from current time
	srand(time(NULL));
	
	// labels stored as a vector
	std::vector<double> labels;
	
	// no. of examples, features in the dataset
	int num_examples, num_features;
	
	/* get size of X (design matrix) */
	num_examples = (int)mxGetM(prhs[0]);
    num_features = (int)mxGetN(prhs[0]);
	
	// examples stored feature-wise, each dimension being a sparse vector
	std::vector<sparse_vector> examples(num_features);
	
	/* fill in 'examples' */
	int curr_index;
	double curr_value;
	double max_value = 0;
    double *ptr = (double *)mxGetPr(prhs[0]);
    for (int i = 0; i < num_features; i++){
		
		sparse_vector& curr_feature = examples[i];
		
        for (int j = 0; j < num_examples; j++){
			curr_index = j;
			curr_value = ptr[i*num_examples + j];
			if(curr_value == 0) continue;
			
			curr_feature.push_back(IndexValuePair(curr_index,curr_value));
			
			//added by Huida:
			if(max_value < fabs(curr_value)){
				max_value = fabs(curr_value);
			}
        }
    }
	 
    
	/* get y (labels) */
    ptr = (double *)mxGetPr(prhs[1]);
    for (int i = 0; i < num_examples; i++){
        labels.push_back(ptr[i]);
    }
	
	/* get lambda, loss_type, num_iters, print_me */
	lambda = *((double *)mxGetPr(prhs[2]));
	loss_type = (int) *((double *)mxGetPr(prhs[3]));
	num_iters = (int) *((double *)mxGetPr(prhs[4]));
	print_me = (int) *((double *)mxGetPr(prhs[5]));
	if(print_me == 0) print_me = num_iters+1;
	
	//Losses L(loss_type); //changed by Huida to :
	Losses L(loss_type, max_value);
	
	
	if(print_me == 1){
		mexPrintf("N=%d, D=%d, maxIter=%d\n", num_examples, num_features, num_iters);
	}
	
	/* Run the stochastic coordinate descent (SCD) algorithm */

	// Initialize weight vector to zero
	std::vector<double> w(num_features,0);
	std::vector<double> innerprod_with_w(num_examples,0);

	double sum, g, eta;
	int i;

	// start a clock
	clock_t start = clock();
	clock_t elapsed = 0;

	// number of accesses to the data matrix
	unsigned long long num_accesses=0;
	
	if(print_me == 1){
		double obj = get_obj(innerprod_with_w,labels,w,num_examples,lambda,L);
		mexPrintf("Initial object function = %f\n", obj);
	}

	for (int iter=0; iter < num_iters; ++iter) {
		
		// update w

#ifdef _GREEDY_
		// choose feature with maximum guaranteed descent
		int best_i;
		double eta_best_i;	

		double predicted_descent;
		double best_descent = -1;

		for (i=0; i<num_features; i++) {

			sum=0;
			for (int j=0; j < examples[i].size(); j++) {
				IndexValuePair ivpair = examples[i][j];
				curr_index = ivpair.first;
				curr_value = ivpair.second;

				sum += L.loss_grad(innerprod_with_w[curr_index], labels[curr_index]) * curr_value;
			}

			num_accesses += examples[i].size();

			g = sum / num_examples;

			if (w[i] - g / L.rho > lambda / L.rho) 
				eta = -g / L.rho - lambda / L.rho;
			else {
				if (w[i] - g / L.rho < -lambda / L.rho)
					eta = -g / L.rho + lambda / L.rho;
				else
					eta = -w[i];
			}
			
			predicted_descent = -eta*g - L.rho / 2 * eta * eta - lambda * fabs(w[i] + eta) + lambda * fabs(w[i]);

			if (predicted_descent > best_descent) {
				best_i = i;
				eta_best_i = eta;
				best_descent = predicted_descent;
			} 
		}

		i = best_i;
		eta = eta_best_i;
#else
#ifdef _CYCLIC_
		// choose feature to update in a cyclic manner
		i = iter % num_features;
#else
		// choose a feature i randomly to update
		i = rand() % num_features;
#endif
		sum=0;
		for (int j=0; j < examples[i].size(); j++) {
			IndexValuePair ivpair = examples[i][j];
			curr_index = ivpair.first;
			curr_value = ivpair.second;

			sum += L.loss_grad(innerprod_with_w[curr_index], labels[curr_index]) * curr_value;
		}

		num_accesses += examples[i].size();

		g = sum / num_examples;

		if (w[i] - g / L.rho > lambda / L.rho) 
			eta = -g / L.rho - lambda / L.rho;
		else {
			if (w[i] - g / L.rho < -lambda / L.rho)
				eta = -g / L.rho + lambda / L.rho;
			else
				eta = -w[i];
		}
#endif
		// update weight vector w
		w[i] = w[i] + eta;

		// update inner products with w
		for (int j=0; j < examples[i].size(); j++) {
			IndexValuePair ivpair = examples[i][j];
			curr_index = ivpair.first;
			curr_value = ivpair.second;

			innerprod_with_w[curr_index] = innerprod_with_w[curr_index] + eta * curr_value;
		}

		num_accesses += examples[i].size();

		// once in a while print the time elapsed, no. of data accesses and the weight vector
		if (iter % print_me == print_me-1) {
		//if (print_me == 1) {
			double obj = get_obj(innerprod_with_w,labels,w,num_examples,lambda,L);
			long time = clock();
			mexPrintf("Iteration %d, clock= %lu object function = %f\n", iter, time, obj);
				
			elapsed += clock() - start;

			
			//std::cout << ( ((double)elapsed/(double)CLOCKS_PER_SEC)*1000 ) << " " << num_accesses << " ";

			// print the summary (1-norm, density, loss, etc.) 
			//print_summary(innerprod_with_w,labels,w,num_examples,lambda,L);
			
			start = clock();
		}

	}
	
		
	/* create return value */
	double *output;
    plhs[0] = mxCreateDoubleMatrix(num_features, 1, mxREAL);
    output = mxGetPr(plhs[0]);
    for(i = 0; i < num_features; i++) output[i] = w[i];
	
	/* clear memory */
	examples.clear();
	labels.clear();
	w.clear();
	innerprod_with_w.clear();
	
}
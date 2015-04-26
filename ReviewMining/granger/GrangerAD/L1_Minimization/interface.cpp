#include "mex.h"
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <fstream>

double **src_data;
double **tgt_data;
double *src_label;
double *alpha;
double C2;
double C3;

double *w;

int nSrc;
int dSrc;
int nTgt;

double  wDivisor;
double  eta0;
double  t;



void mexFunction(int nlhs, mxArray *plhs[ ], int nrhs, const mxArray *prhs[ ]) {
    // The order of input
    // (1) src samples, (2) src labels, (3) tgt samples, (4) alpha, (5) alpha_b, (6) C2, (7) C3
    // Src samples: n x d array
    // Src labels: n x 1 array
    // Tgt samples: m x d array
    // Alpha: d x 1 array
    // Example in Matlab: [w b] = sgdTSVM(src, lbl, tgt, wInit, alpha, alpha_b, C2, C3, nIter, nTune)
    int i = 0;
    int j = 0;
    //srand48(time(NULL)); ------------------------------------------------------
    
    /*------------------Get Source Samples-------------------------------*/
    nSrc = mxGetM(prhs[0]);
    dSrc = mxGetN(prhs[0]);
    
    src_data = new double*[nSrc];
    for (i = 0; i < nSrc; i++){ src_data[i] = new double[dSrc+1]; }
    
    double *ptr = (double *)mxGetPr(prhs[0]);
    for (i = 0; i < dSrc; i++){
        for (j = 0; j < nSrc; j++){
            src_data[j][i] = ptr[i*nSrc + j];
        }
    }
    for (i = 0; i < nSrc; i++){ 
        src_data[i][dSrc] = 1;}
    /*-------------------Get Source Labels-------------------------------*/
    src_label = new double[nSrc];
    ptr = (double *)mxGetPr(prhs[1]);
    for (i = 0; i < nSrc; i++){
        src_label[i] = ptr[i];
    }
    /*------------------Get Target Samples-------------------------------*/
    nTgt = mxGetM(prhs[2]);
    
    tgt_data = new double*[nTgt];
    for (i = 0; i < nTgt; i++){ tgt_data[i] = new double[dSrc+1]; }
    
    ptr = (double *)mxGetPr(prhs[2]);
    for (i = 0; i < dSrc; i++){
        for (j = 0; j < nTgt; j++){
            tgt_data[j][i] = ptr[i*nTgt + j];
        }
    }
    for (i = 0; i < nTgt; i++){ 
        tgt_data[i][dSrc] = 1;}
    /*------------------set Initial w -----------------------------------*/
    w = new double[dSrc+1];
    ptr = (double *)mxGetPr(prhs[3]);
    for (i = 0; i <= dSrc; i++){
        w[i] = ptr[i];
    }
    
//     /*---------------------------Get Alpha-------------------------------*/
//     alpha = new double[dSrc+1];
//     ptr = (double *)mxGetPr(prhs[4]);
//     for (i = 0; i <= dSrc; i++){
//         alpha[i] = ptr[i];
//     }
//     /*---------------------------The rest--------------------------------*/
//     C2 = *((double *)mxGetPr(prhs[5]));
//     C3 = *((double *)mxGetPr(prhs[6]));
//     int max_rounds = *((int *)mxGetPr(prhs[7]));
//     double ratio = *((double *)mxGetPr(prhs[8]));
//     
//     t = 0;
//     wDivisor = 1;
    /*---------------------------------------------------------------------
     *------------------------MAIN TRAINING--------------------------------
     *---------------------------------------------------------------------
     */
    
    /* --- determine the Eta0, using a subset of src_data, which consists of src_data[imin...imax] --- */
    for (i=0; i<nSrc; i++){
        for (j=0; j<dSrc; j++){
            mexPrintf("%f\t", src_data[i][j]);
        }
        mexPrintf("\n");
    }
    /*---------------------------------------------------------------------
     *---------------------------OUTPUTTING--------------------------------
     *---------------------------------------------------------------------
     */
    
    double *output;
    plhs[0] = mxCreateDoubleMatrix(1, dSrc, mxREAL);
    output = mxGetPr(plhs[0]);
    
    memcpy(output, w, dSrc*sizeof(double));
    
    plhs[1] = mxCreateDoubleMatrix(1, 1, mxREAL);
    output = mxGetPr(plhs[1]);
    memcpy(output, &(w[dSrc]), sizeof(double));
    /*---------------------------------------------------------------------
     *---------------------------------------------------------------------
     *---------------------------------------------------------------------
     */
    for (i = 0; i < nSrc; i++)
        delete [] src_data[i];
    delete [] src_data;
    
    delete [] src_label;
    
    for (i = 0; i < nTgt; i++)
        delete [] tgt_data[i];
    delete [] tgt_data;
    
// //     delete [] tgt_label;
//     delete [] alpha;
//     delete [] w;
    
    return;
    
}
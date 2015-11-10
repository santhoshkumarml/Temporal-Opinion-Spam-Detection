#ifndef _SHAI_LOSSES_H_
#define _SHAI_LOSSES_H_

#include <cstdlib>
#include <cmath>

typedef unsigned int uint;

double logistic_loss(double a, double b) {
  if (a <= 10.0 && a >= -10.0) 
    return(log(1+exp(-a*b)));
  else {
    if (a*b > 0.0) 
      return(0.0);
    else
      return(-a*b);
  }
}

double logistic_loss_grad(double a, double b) {
  if (a <= 10.0 && a >= -10.0) 
    return(-b/(1+exp(a*b)));
  else {
    if (a*b > 0.0)
      return(0.0);
    else
      return(-b);
  }
}


double quadratic_loss(double a, double b) {
  return(0.5*(a-b)*(a-b));
}

double quadratic_loss_grad(double a, double b) {
  return (a-b);
}

double hinge_loss(double a, double b) {
  double margin = 1-a*b;
  if (margin < 0.0) margin = 0.0;
  return(margin);
}

double hinge_loss_grad(double a, double b) {
  double g=0.0;
  if (a*b < 1) g=-b;
  return(g);
}

class Losses {

 public:
 Losses(int loss_type) : 
  type(loss_type), my_loss(&logistic_loss), my_grad_loss(&logistic_loss_grad), rho(0.25) {
    if (type == 1) {
      my_loss = &hinge_loss;
      my_grad_loss = &hinge_loss_grad;
    } else if (type == 2) {
      my_loss = &quadratic_loss;
      my_grad_loss = &quadratic_loss_grad;
      rho = 1;
    } 
  }
  
  //added by Huida to deal with unnormalized input data: (examples are in the range [-r,r])
  Losses(int loss_type, double r) : 
  type(loss_type), my_loss(&logistic_loss), my_grad_loss(&logistic_loss_grad), rho(0.25*r*r) {
    if (type == 1) {
      my_loss = &hinge_loss;
      my_grad_loss = &hinge_loss_grad;
    } else if (type == 2) {
      my_loss = &quadratic_loss;
      my_grad_loss = &quadratic_loss_grad;
      rho = r*r;
    } 
  }

  double rho;

  double loss(double a,double b) {
    return((*my_loss)(a,b));
  }

  double loss_grad(double a,double b) {
    return((*my_grad_loss)(a,b));
  }

  int get_type(){
	  return type;
  }
  
  ~Losses() { }

 protected:
  int type;
  double (*my_loss)(double,double);  
  double (*my_grad_loss)(double,double);  
};

#endif
//*****************************************************************************
//                                     E O F
//*****************************************************************************

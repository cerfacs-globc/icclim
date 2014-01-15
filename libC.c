#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// gcc -fPIC -g -c -Wall libC.c
// gcc -shared -o libC.so libC.o

// Global variables
int sizeT,sizeI,sizeJ;


void setGlobalVariables(int _sizeT,int _sizeI,int _sizeJ){
    sizeT = _sizeT;
    sizeI = _sizeI;
    sizeJ = _sizeJ;
}

//double getElementAt(const double *table, int t, int i, int j){
double getElementAt(const float *table, int t, int i, int j){
    return table[t*sizeI*sizeJ + i*sizeJ +j];
}




// ERROR 3
//Segmentation fault (core dumped)
//http://stackoverflow.com/questions/13654449/error-segmentation-fault-core-dumped

int find_max_len_consec_sequence_1d(const float *indata,int i, int j, float thresh, float fill_val, char *operation)
    {
    // find max length of a consecutif sequence in 1D array in a chosen logical condition ("gt", "get", "lt", "let", "e")
        float previous=-999;
        int nb_max=0;
        int nb=0;
        int t;
        
        //printf ("AAAAA");
        
        ///////////   >
        if (strcmp(operation,"gt")==0)
            {
        
                for (t = 0; t < sizeT; t++)
                    {
                        //double val = getElementAt(indata,t,i,j);
                        float val = getElementAt(indata,t,i,j);
        
                        if ((val>thresh) && (val != fill_val))
                            {
                                if (previous>thresh) nb++;
                                else nb=1;	    
                            }
                        else nb=0;
                        
                        
                        
                        if (nb>nb_max) nb_max=nb;
                        
                        previous=val;
                    }
            }
        
        ///////////   >=    
        else if (strcmp(operation,"get")==0)
            {
        
                for (t = 0; t < sizeT; t++)
                    {
                        //double val = getElementAt(indata,t,i,j);
                        float val = getElementAt(indata,t,i,j);
        
                        if ((val>=thresh) && (val != fill_val))
                            {
                                if (previous>=thresh) nb++;
                                else nb=1;	    
                            }
                        else nb=0;
                        
                        
                        
                        if (nb>nb_max) nb_max=nb;
                        
                        previous=val;
                    }
            }    
        
        ///////////   <
        else if (strcmp(operation,"lt")==0)
            {
        
                for (t = 0; t < sizeT; t++)
                    {
                        //double val = getElementAt(indata,t,i,j);
                        float val = getElementAt(indata,t,i,j);
        
                        if ((val<thresh) && (val != fill_val))
                            {
                                if (previous<thresh) nb++;
                                else nb=1;	    
                            }
                        else nb=0;
                        
                        
                        
                        if (nb>nb_max) nb_max=nb;
                        
                        previous=val;
                    }
            }
        
        ///////////   <=
        else if (strcmp(operation,"let")==0)
            {
        
                for (t = 0; t < sizeT; t++)
                    {
                        //double val = getElementAt(indata,t,i,j);
                        float val = getElementAt(indata,t,i,j);
        
                        if ((val<=thresh) && (val != fill_val))
                            {
                                if (previous<=thresh) nb++;
                                else nb=1;	    
                            }
                        else nb=0;
                        
                        
                        
                        if (nb>nb_max) nb_max=nb;
                        
                        previous=val;
                    }
            }
        
        ///////////   =
        else if (strcmp(operation,"e")==0)
            {
        
                for (t = 0; t < sizeT; t++)
                    {
                        //double val = getElementAt(indata,t,i,j);
                        float val = getElementAt(indata,t,i,j);
        
                        if ((val==thresh) && (val != fill_val))
                            {
                                if (previous==thresh) nb++;
                                else nb=1;	    
                            }
                        else nb=0;
                        
                        
                        
                        if (nb>nb_max) nb_max=nb;
                        
                        previous=val;
                    }
            }
            
        return nb_max;
    
    }


// fonction appelee depus python in CSU_arr_C
void find_max_len_consec_sequence_3d(const float *indata, int _sizeT,int _sizeI,int _sizeJ, double *outdata, float temp, float fill_val, char *operation) 
    {
    // find max length of a consecutif sequence in 3D array (along time axis) in a logical condition
    
        //outdata = (double *) malloc (_sizeI*_sizeJ*sizeof(double));
        setGlobalVariables(_sizeT,_sizeI,_sizeJ);
        int i,j;
        //printf("coucou");
            for (i = 0; i < sizeI; i++)
                {
                    for (j = 0; j < sizeJ; j++)
                        {
                            //outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,temp);
                            outdata[i*sizeJ+j] = find_max_len_consec_sequence_1d(indata,i,j,temp, fill_val, operation); 
                        }
                }
    }
    


    
//void main(){
//    
//    //char *lettre = 'ab';
//    //little2BIG(lettre);
//    
//    printf('HELLO WORLD !!!')
//     
//    
//}
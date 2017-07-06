#include "./libPerso.h"
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <TString.h>
#include <iostream>
#include <iomanip>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <vector>
#include <utility>

using namespace std;

int rdn(int y, int m, int d) { /* Rata Die day one is 0001-01-01 */
   if (m < 3)
   y--, m += 12;
   return 365*y + y/4 - y/100 + y/400 + (153*m - 457)/5 + d - 306;
}

TString sec_to_time(float totaltime){
   int hours = totaltime/3600;
   float minutesRemainder = (totaltime - hours*3600) / 60;
   int minutes = minutesRemainder;
   float secondsRemainder = (minutesRemainder*60 - minutes*60);
   int seconds = secondsRemainder;
   TString times="";
   times.Form("%d:%d:%d", hours, minutes, seconds);
   return times;
}

void plot_histo(const char *path, const char *LEMnumber, const char *nlines, const char *nlineshort){

   TString inputshortVdet = path;
   TString inputVdet = path;
   TString inputSpT0 = path;
   TString pdfhistoVdet = path;
   TString pdfhistoI = path;
   TString pdfhistoSpT1 = path;
   TString pdfhistoSpT1vsVdet = path;
   TString ChistoVdet = path;
   TString ChistoI = path;
   TString ChistoSpT1 = path;
   TString ChistoSpT1vsVdet = path;
   inputshortVdet.Append("shortVdet");
   inputVdet.Append("DVDet");
   inputSpT0.Append("SpT0");
   pdfhistoVdet.Append("Vdet.pdf");
   pdfhistoI.Append("I.pdf");
   pdfhistoSpT1.Append("SpT1.pdf");
   pdfhistoSpT1vsVdet.Append("SpT1vsVdet.pdf");
   ChistoVdet.Append("Vdet.C");
   ChistoI.Append("I.C");
   ChistoSpT1.Append("SpT1.C");
   ChistoSpT1vsVdet.Append("SpT1vsVdet.C");

   int count=0;
   int lines=atoi(nlines);
   int lineshort=atoi(nlineshort);
   fstream infileshortVdet;
   fstream infileVdet;
   fstream infileSpT0;

   TH1D* h_VdetT=new TH1D("Vdet","Vdet",lines-1,0,(lines-2)/3600);
   TH1D* h_ImonT=new TH1D("Imon","Imon",lines-1,0,(lines-2)/3600);
   TH1D* h_SpT1T=new TH1D("SpT1","SpT1",lines-1,0,(lines-2)/3600);

   string strVdet, strVset, strI, strHeure, strSpT1, tmDate, checktime;
   float vup, vdown;
   float Vdet, I, SpT1, real_SpT1;
   TString time0;
   TString strDate;
   float tmp_Vdet=0.0;
   float tmp_Vup=0.0;
   float tmp_Vdown=0.0;
   float tmp_SpT1=0.0;
   float tmp_ratio=0.0;
   float junk;
   float ratioV=0;
   float starttime=0;
   float totaltime=0;
   float time0_0=0;
   float time0_1=0;
   float timeadd=0;
   float timemin=600;
   float yy, mm, dd, tmpyy, tmpmm, tmpdd, h, m, s, hstart, mstart, sstart, hend, mend, send;
   bool check=false;
   bool isempty=false;
   vector <float> vecVdet;
   vector <float> vecSpT1;
   vector <float> var_vecSpT1;
   vector <TString> vectimes;

   infileshortVdet.open(inputshortVdet.Data(),fstream::in);
   infileVdet.open(inputVdet.Data(),fstream::in);
   infileSpT0.open(inputSpT0.Data(),fstream::in);
   if(!infileshortVdet.is_open()){cout<<"Error opening "<<inputshortVdet.Data()<<" file"<<endl; return;}
   if(!infileVdet.is_open()){cout<<"Error opening "<<inputVdet.Data()<<" file"<<endl; return;}
   if(!infileSpT0.is_open()){cout<<"Error opening "<<inputSpT0.Data()<<" file"<<endl; return;}
   infileSpT0.seekg(0,ios::end);
   int length=infileSpT0.tellg();
   if(length==0){
      isempty=true;
   }
   infileSpT0.close();
   infileSpT0.open(inputSpT0.Data(),fstream::in);

   while(!infileshortVdet.eof()){
      infileshortVdet>>junk>>junk>>junk>>vup>>vdown>>strDate>>time0>>SpT1>>checktime;
      sscanf(strDate.Data(),"%f_%f_%f",&yy,&mm,&dd);
      sscanf(time0.Data(),"%f:%f:%f",&h,&m,&s);
      Vdet=vdown-vup;
      ratioV=vdown/vup;
      if(count==0){
         starttime=3600*h+60*m+s;
         tmpdd=dd;
         tmpmm=mm;
         tmpyy=yy;
      }
      else if(count==1){
         timeadd+=(rdn(yy, mm, dd) - rdn(tmpyy, tmpmm, tmpdd))*24*3600;
         time0_0=3600*h+60*m+s+timeadd;
         tmpdd=dd;
         tmpmm=mm;
         tmpyy=yy;
         tmp_Vdet=Vdet;
         tmp_SpT1=SpT1;
         tmp_ratio=ratioV;
         tmp_Vup=vup;
         tmp_Vdown=vdown;
         real_SpT1=SpT1;
      }
      else if(count>1){
         timeadd+=(rdn(yy, mm, dd) - rdn(tmpyy, tmpmm, tmpdd))*24*3600;
         time0_1=3600*h+60*m+s+timeadd;
         //if another spark at same tension, after 30s from previous
         if(abs(time0_1-time0_0) > 3 && tmp_Vup==vup && tmp_Vdown==vdown && checktime=="chien"){
            real_SpT1+=SpT1;
            check=true;
         }
         //if another spark at same tension, before 30s from previous
         else if(abs(time0_1-time0_0) < 3 && SpT1>tmp_SpT1 && tmp_Vup==vup && tmp_Vdown==vdown && checktime=="chien"){
            real_SpT1+=SpT1-tmp_SpT1;
            check=true;
         }
         else if (checktime=="begin") {
            starttime=time0_1-timeadd;
            timeadd=0;
         }
         else if (checktime=="end") {
            if(count==lineshort){
               break;
            }
            totaltime+=time0_1-starttime;
         }
         //if voltage diff changed and previous one is not transitory
         else if((tmp_Vup!=vup || tmp_Vdown!=vdown) && checktime=="chien" && totaltime>timemin){
            vecSpT1.push_back(3600*real_SpT1/totaltime);
            var_vecSpT1.push_back(TMath::Sqrt(3600*real_SpT1/totaltime));
            vecVdet.push_back(tmp_Vdet);
            vectimes.push_back(sec_to_time(totaltime));
            totaltime=0;
            real_SpT1=SpT1;
            check=true;
         }
         else if((tmp_Vup!=vup || tmp_Vdown!=vdown) && checktime=="chien" && totaltime<timemin){
            check=true;
         }
         if (check) {
            tmp_Vup=vup;
            tmp_Vdown=vdown;
            tmp_Vdet=Vdet;
            tmp_SpT1=SpT1;
            tmp_ratio=ratioV;
         }
         time0_0=time0_1;
         tmpdd=dd;
         tmpmm=mm;
         tmpyy=yy;
         check=false;
      }
      count++;
   }
   infileshortVdet.close();
   count=0;
   if(totaltime>timemin){
      vecSpT1.push_back(3600*real_SpT1/totaltime);
      var_vecSpT1.push_back(3600*TMath::Sqrt(real_SpT1)/totaltime);
      vecVdet.push_back(tmp_Vdet);
      vectimes.push_back(sec_to_time(totaltime));
   }

   if(vecVdet.size()==0){
      cout<<"No spark on this run and/or acquisition time too short"<<endl;
      return;
   }
   if(!isempty){
      while(!infileSpT0.eof()){
         infileSpT0>>vup>>vdown;
         Vdet=vdown-vup;
         vecVdet.push_back(Vdet);
         vecSpT1.push_back(0);
         var_vecSpT1.push_back(0);
         vectimes.push_back(" ");
         //cout<<Vdet<<" "<<vecSpT1[vecSpT1.size()-1]<<"+/-"<<var_vecSpT1[var_vecSpT1.size()-1]<<" "<<sec_to_time(totaltime)<<endl;
      }
      infileSpT0.close();
   }

   for(int i=0;i<vecVdet.size()-1;i++){
      for(int j=0;j<vecVdet.size()-1;j++){
         float tmpv1=vecVdet[j];
         float tmpv2=vecVdet[j+1];
         float tmpspt1=vecSpT1[j];
         float tmpspt2=vecSpT1[j+1];
         float tmpvar1=var_vecSpT1[j];
         float tmpvar2=var_vecSpT1[j+1];
         TString tmptime1=vectimes[j];
         TString tmptime2=vectimes[j+1];
         if (tmpv1>tmpv2){
            vecVdet[j+1]=tmpv1;
            vecVdet[j]=tmpv2;
            vecSpT1[j+1]=tmpspt1;
            vecSpT1[j]=tmpspt2;
            var_vecSpT1[j+1]=tmpvar1;
            var_vecSpT1[j]=tmpvar2;
            vectimes[j+1]=tmptime1;
            vectimes[j]=tmptime2;
         }
      }
   }
   for(int i=0;i<vecVdet.size();i++){
      cout<<vecVdet[i]<<" "<<vecSpT1[i]<<"+/-"<<var_vecSpT1[i]<<" "<<vectimes[i]<<endl;
   }

   while(!infileVdet.eof()){
      if(count==0){
         infileVdet>>strI>>strVdet>>strVdet>>strVset>>strVset>>strDate>>strHeure>>strSpT1;
      }
      else{
         infileVdet>>I>>junk>>junk>>vup>>vdown>>strDate>>time0>>SpT1;
         Vdet=vdown-vup;
         h_VdetT->SetBinContent(count,Vdet/1000.);
         h_ImonT->SetBinContent(count,I/1000.);
         h_SpT1T->SetBinContent(count,SpT1);
      }
      count++;
   }
   infileVdet.close();

   TGraphErrors *gr_SpT1_vs_Vset = new TGraphErrors(vecVdet.size(),&(vecVdet[0]),&(vecSpT1[0]),0,&var_vecSpT1[0]);

   int npoints = gr_SpT1_vs_Vset->GetN();
   int j=0;
   Double_t x,y;
   float *Y=gr_SpT1_vs_Vset->GetY();
   float max=TMath::LocMax(npoints,Y);

   gStyle->SetOptStat(0);
   gStyle->SetTitleFontSize(0.08);
   TCanvas *canVdet=new TCanvas("Vdet","Vdet",1500,1000);
   TString title="LEM ";
   title.Append(LEMnumber);
   title.Append(";time(h);Voltage(kV)");
   h_VdetT->SetTitle(title.Data());
   h_VdetT->SetTitleSize(0.06,"X");
   h_VdetT->SetTitleSize(0.06,"Y");
   h_VdetT->GetXaxis()->SetTitleOffset(0.7);
   h_VdetT->GetYaxis()->SetTitleOffset(0.6);
   h_VdetT->Draw();
   canVdet->Print(pdfhistoVdet.Data());
   canVdet->SaveAs(ChistoVdet.Data());

   TCanvas *canI=new TCanvas("Imon","Imon",1500,1000);
   title="LEM ";
   title.Append(LEMnumber);
   title.Append(";time(h);Current(mA)");
   h_ImonT->SetTitle(title.Data());
   h_ImonT->SetTitleSize(0.06,"X");
   h_ImonT->SetTitleSize(0.06,"Y");
   h_ImonT->GetXaxis()->SetTitleOffset(0.7);
   h_ImonT->GetYaxis()->SetTitleOffset(0.6);
   h_ImonT->Draw();
   canI->Print(pdfhistoI.Data());
   canI->SaveAs(ChistoI.Data());

   TCanvas *canSpT1vsVdet=new TCanvas("SpT1vsVdet","SpT1vsVdet",1500,1000);
   title="LEM ";
   title.Append(LEMnumber);
   title.Append(";Vset(V);Spark per hour");
   gr_SpT1_vs_Vset->SetTitle(title.Data());
   gr_SpT1_vs_Vset->SetName(title.Data());
   gr_SpT1_vs_Vset->SetMinimum(0);
   gr_SpT1_vs_Vset->SetMarkerStyle(34);
   gr_SpT1_vs_Vset->SetMarkerColor(1);
   gr_SpT1_vs_Vset->SetMarkerSize(2);
   gr_SpT1_vs_Vset->SetLineColor(1);
   gr_SpT1_vs_Vset->GetXaxis()->SetTitleSize(0.05);
   gr_SpT1_vs_Vset->GetYaxis()->SetTitleOffset(0.6);
   gr_SpT1_vs_Vset->GetYaxis()->SetTitleSize(0.075);
   gr_SpT1_vs_Vset->GetYaxis()->SetLabelSize(0.045);
   gr_SpT1_vs_Vset->Draw("AP");
   canSpT1vsVdet->Update();
   double ymax=gPad->GetUymax();
   double ymin=gPad->GetUymin();
   double Range=ymax-ymin;
   //cout<<ymax<<" "<<ymin<<" "<<Range<<endl;
   for (int i=0; i<npoints; i++) {
      gr_SpT1_vs_Vset->GetPoint(i,x,y);
      if(i%2){
         //cout<<x<<" "<<y<<endl;
         TLatex* l = new TLatex(x,y+0.03*Range,vectimes[i].Data());
      }
      else{
         TLatex* l = new TLatex(x,y-0.04*Range,vectimes[i].Data());
      }
      l->SetTextSize(0.025);
      l->SetTextColor(4);
      l->SetTextFont(42);
      l->SetTextAlign(21);
      l->Draw("SAME");
   }
   canSpT1vsVdet->Print(pdfhistoSpT1vsVdet.Data());
   canSpT1vsVdet->SaveAs(ChistoSpT1vsVdet.Data());

   return;
}

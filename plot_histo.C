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
#include <sstream>
#include <string>

using namespace std;

void plot_histo(const char *globdirname, const char *analysedirname){

  TString dirname = TString(globdirname) + TString(analysedirname);
  fstream sparks, lemlist, sparknumber_file;
  TString lemlist_path = dirname + "lemlist";
  TString sparks_path = dirname + "sparks";
  TString sparknumber_path = dirname + "sparknumber";
  lemlist.open(lemlist_path.Data(), fstream::in);
  sparknumber_file.open(sparknumber_path.Data(), fstream::in);
  int sparknumber;
  float maxV = -10000;
  float maxI = -10000;
  float minV = 10000;
  float minI = 10000;
  sparknumber_file>>sparknumber;
  vector<TString> LEMs;
  int LEMnumber = 0;
  while(!lemlist.eof()){
    LEMnumber++;
    TString lem = "";
    lemlist>>lem;
    LEMs.push_back(lem);
  }
  lemlist.close();
  LEMnumber--;
  LEMs.pop_back();
  sparks.open(sparks_path.Data(), fstream::in);
  string line;
  int linenumber = 0;
  for(int i = 0; getline(sparks, line); ++i){
    linenumber++;
  }
  sparks.close();
  sparks.open(sparks_path.Data(), fstream::in);
  vector<int> col;
  col.push_back(1); col.push_back(618); col.push_back(600); col.push_back(632); col.push_back(416); col.push_back(400);
  gStyle->SetOptStat(0);
  for(int j = 0; j < linenumber; j++){
    float floatspark;
    stringstream stringV;
    float vset, SPH/*, ssph*/;
    sparks>>vset;
    stringV<<vset;
    TH1D *histo = new TH1D("","",LEMnumber, 0, LEMnumber);
    for(int i = 0; i < LEMnumber; i++){
      sparks>>floatspark;
      histo->SetBinContent(i+1,floatspark);
      histo->SetLineWidth(3);
      histo->GetXaxis()->SetBinLabel(i+1, LEMs[i].Data());
    }
    TCanvas *Sparkcan = new TCanvas("Sparkcan","Sparkcan",2000,1700);
    histo->Draw();
    histo->GetXaxis()->SetTitle("LEM");
    histo->GetYaxis()->SetTitle("Sparks per hour");
    TString title = TString(analysedirname) + TString(stringV.str()) + "V";
    histo->SetTitle(title.Data());
    TString Spath = dirname + TString(stringV.str()) + TString("sparks.pdf");
    Sparkcan->SaveAs(Spath.Data());
    delete Sparkcan;
    delete histo;
  }
  sparks.close();

  //All V and I
  vector<TGraph*> graphsV;
  vector<TGraph*> graphsI;
  vector<int> col;
  col.push_back(1); col.push_back(618); col.push_back(600); col.push_back(632); col.push_back(416); col.push_back(400);
  TLegend *legV = new TLegend(0.85,0.7,0.95,0.95);
  TLegend *legI = new TLegend(0.85,0.7,0.95,0.95);
  for (int i = 0; i<LEMnumber; i++){
    TString lempath = TString(dirname) + LEMs[i] + "/lemdata";
    TGraph *lemgraphV = new TGraph(lempath.Data());
    if(maxV < TMath::MaxElement(lemgraphV->GetN(),lemgraphV->GetY()) ){maxV = TMath::MaxElement(lemgraphV->GetN(),lemgraphV->GetY());}
    if(minV > TMath::MinElement(lemgraphV->GetN(),lemgraphV->GetY()) ){minV = TMath::MinElement(lemgraphV->GetN(),lemgraphV->GetY());}
    lemgraphV->SetLineColor(col[i]);
    lemgraphV->SetLineWidth(3);
    legV->AddEntry(lemgraphV, LEMs[i].Data(), "l");
    graphsV.push_back(lemgraphV);
    TGraph *lemgraphI = new TGraph(lempath.Data(),"%lg %*lg %lg");
    if(maxI < TMath::MaxElement(lemgraphI->GetN(),lemgraphI->GetY()) ){maxI = TMath::MaxElement(lemgraphI->GetN(),lemgraphI->GetY());}
    if(minI > TMath::MinElement(lemgraphI->GetN(),lemgraphI->GetY()) ){minI = TMath::MinElement(lemgraphI->GetN(),lemgraphI->GetY());}
    lemgraphI->SetLineColor(col[i]);
    lemgraphI->SetLineWidth(3);
    legI->AddEntry(lemgraphI, LEMs[i].Data(), "l");
    graphsI.push_back(lemgraphI);
  }
  TCanvas *Vcan = new TCanvas("Vcan","Vcan",2000,1700);
    for(int i = 0; i < graphsV.size(); i++){
      if(i==0){
        graphsV[i]->Draw();
        graphsV[i]->GetXaxis()->SetTitle("Time (hours)");
        graphsV[i]->GetYaxis()->SetTitle("Voltage (V)");
        graphsV[i]->SetTitle(analysedirname);
      }
      else{graphsV[i]->Draw("SAME");}
    }
    legV->Draw();
  TString Vpath = dirname + TString("voltages.pdf");
  Vcan->SaveAs(Vpath.Data());
  TCanvas *Ican = new TCanvas("Ican","Ican",2000,1700);
    for(int i = 0; i < graphsI.size(); i++){
      if(i==0){
        graphsI[i]->Draw();
        graphsI[i]->GetXaxis()->SetTitle("Time (hours)");
        graphsI[i]->GetYaxis()->SetTitle("Current");
        graphsI[i]->SetTitle(analysedirname);
      }
      else{graphsI[i]->Draw("SAME");}
    }
    legI->Draw();
  TString Ipath = dirname + TString("currents.pdf");
  Ican->SaveAs(Ipath.Data());
  
  
  //All V and I at sparks
  for (int j = 0; j < sparknumber; j++){
    vector<TGraph*> graphssparkV;
    vector<TGraph*> graphssparkI;
    TLegend *legsparkV = new TLegend(0.85,0.7,0.95,0.95);
    TLegend *legsparkI = new TLegend(0.85,0.7,0.95,0.95);
    for (int i = 0; i<LEMnumber; i++){
      TString sparkpath = TString(dirname) + LEMs[i] + "/sparks/" + TString::Format("sp%i",j);
      TGraph *sparkgraphV = new TGraph(sparkpath.Data());
      sparkgraphV->SetLineColor(col[i]);
      sparkgraphV->SetLineWidth(3);
      legsparkV->AddEntry(sparkgraphV, LEMs[i].Data(), "l");
      graphssparkV.push_back(sparkgraphV);
      TGraph *sparkgraphI = new TGraph(sparkpath.Data(),"%lg %*lg %lg");
      sparkgraphI->SetLineColor(col[i]);
      sparkgraphI->SetLineWidth(3);
      legsparkI->AddEntry(sparkgraphI, LEMs[i].Data(), "l");
      graphssparkI.push_back(sparkgraphI);
    }
    TCanvas *sparkVcan = new TCanvas("sparkVcan","sparkVcan",2000,1700);
      for(int i = 0; i < graphssparkV.size(); i++){
        if(i==0){
          graphssparkV[i]->SetMaximum(maxV);
          graphssparkV[i]->SetMinimum(minV);
          graphssparkV[i]->Draw();
          graphssparkV[i]->GetXaxis()->SetTitle("Time (hours)");
          graphssparkV[i]->GetYaxis()->SetTitle("Voltage (V)");
          graphssparkV[i]->SetTitle(analysedirname);
        }
        else{graphssparkV[i]->Draw("SAME");}
      }
      legsparkV->Draw();
      TString sparkVpath = dirname + TString::Format("Voltages_sp%i",j) + TString(".pdf");
    sparkVcan->SaveAs(sparkVpath.Data());
    delete sparkVcan;
    TCanvas *sparkIcan = new TCanvas("sparkIcan","sparkIcan",2000,1700);
      for(int i = 0; i < graphssparkI.size(); i++){
        if(i==0){
          graphssparkI[i]->SetMaximum(maxI);
          graphssparkI[i]->SetMinimum(minI);
          graphssparkI[i]->Draw();
          graphssparkI[i]->GetXaxis()->SetTitle("Time (hours)");
          graphssparkI[i]->GetYaxis()->SetTitle("Current");
          graphsI[i]->SetTitle(analysedirname);
        }
        else{graphssparkI[i]->Draw("SAME");}
      }
      legsparkI->Draw();
      TString sparkIpath = dirname + TString::Format("Currents_sp%i",j) + TString(".pdf");
    sparkIcan->SaveAs(sparkIpath.Data());
    delete sparkIcan;
  }
  
  //Single V and I
  for(int i = 0; i < graphsV.size(); i++){
    TCanvas *Vcansolo = new TCanvas("","",2000,1700);
      graphsV[i]->Draw();
      graphsV[i]->GetXaxis()->SetTitle("Time (hours)");
      graphsV[i]->GetYaxis()->SetTitle("Voltage (V)");
      TString title = TString(analysedirname) + LEMs[i];
      graphsV[i]->SetTitle(title.Data());
      TString Vpathsolo = dirname + LEMs[i] + "/" + LEMs[i] + TString("voltage.pdf");
    Vcansolo->SaveAs(Vpathsolo.Data());
    delete Vcansolo;
  }
  
  for(int i = 0; i < graphsI.size(); i++){
    TCanvas *Icansolo = new TCanvas("","",2000,1700);
      graphsI[i]->Draw();
      graphsI[i]->GetXaxis()->SetTitle("Time (hours)");
      graphsI[i]->GetYaxis()->SetTitle("Current");
      TString title = TString(analysedirname) + LEMs[i];
      graphsI[i]->SetTitle(title.Data());
      TString Ipathsolo = dirname + LEMs[i] + "/" + LEMs[i] + TString("current.pdf");
    Icansolo->SaveAs(Ipathsolo.Data());
    delete Icansolo;
  }

  return;
}

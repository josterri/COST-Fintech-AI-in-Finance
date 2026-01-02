data<-read.csv("/Users/liuyiting/Downloads/COST FinAI GP3 Attendance - Results - 第 1 张表单回复-2.csv",header=T)
head(data)
colnames(data)[1]
data[1,1]
pos<-c("in-person attendance","online")
Brussels<-data[((data$X5..COST.FinAI.Meets.Brussels..https...www.meetup.com.fintech_ai_in_finance.events.289811055..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..May.15..2023....May.16..2023.Brussels..Belgium..2023.05.15.%in%pos) *
  (data$X5..COST.FinAI.Meets.Brussels..https...www.meetup.com.fintech_ai_in_finance.events.289811055..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..May.15..2023....May.16..2023.Brussels..Belgium..2023.05.16.%in%pos) >0)
     ,c(3,2)]
Twente<-data[((data$X9..Fintech.and.AI.in.Finance.Training.School.https...www.meetup.com.fintech_ai_in_finance.events.289810679..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..June.12..2023....June.16..2023.Enschede..Netherlands..2023.06.12.%in%pos) *
                (data$X9..Fintech.and.AI.in.Finance.Training.School.https...www.meetup.com.fintech_ai_in_finance.events.289810679..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..June.12..2023....June.16..2023.Enschede..Netherlands..2023.06.13.%in%pos)*
                (data$X9..Fintech.and.AI.in.Finance.Training.School.https...www.meetup.com.fintech_ai_in_finance.events.289810679..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..June.12..2023....June.16..2023.Enschede..Netherlands..2023.06.14.%in%pos)*
                (data$X9..Fintech.and.AI.in.Finance.Training.School.https...www.meetup.com.fintech_ai_in_finance.events.289810679..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..June.12..2023....June.16..2023.Enschede..Netherlands..2023.06.15.%in%pos)*
                (data$X9..Fintech.and.AI.in.Finance.Training.School.https...www.meetup.com.fintech_ai_in_finance.events.289810679..Main.contact..Joerg.Osterrieder..joerg.osterrieder.bfh.ch..June.12..2023....June.16..2023.Enschede..Netherlands..2023.06.16.%in%pos)
              >0)
             ,c(3,2)]
library(car)
Export(Brussels,"/Users/liuyiting/Downloads/Brussels.xlsx",format = "xlsx")
Export(Twente,"/Users/liuyiting/Downloads/Twente.xlsx",format = "xlsx")




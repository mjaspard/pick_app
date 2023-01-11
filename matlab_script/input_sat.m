function [SAT,MODE,incid,azim,slra]=input_sat(k)
toto = {
    "Sentinel--1" , "Ascending Right" ,14.05 ,2.33 ,34.02 ; % 1
    "Sentinel--1", "Descending Right"  ,14.05 ,2.33 ,39.36 ; % 2
    "CSK", "Ascending Right" , 2.26,1.25 , 34.95; % 3
    "CSK", "Descending Right" , 2.21,0.93 , 26.09; % 4
    "ALOS 2", "Ascending Right" , 13.06, 8.58, 40.18; % 5
    "ALOS 2", "Descending Right"  , 13, 8.6,41 ; % 6
    "Capella","Ascending Left",1.66,1.5 ,30.23 ;% 7
    "Capella", "Ascending Left" ,  1.66, 1.64, 34.4;% 8
    "RCM", "Descending Right"  , 1.25, 0.82, 40.75 ;% 9
    "RCM", "Ascending Right" ,1.25 , 0.83, 41.5;% 10
    "RCM", "Ascending Right"  , 1.25,1 , 53.5;% 11
    "SAOCOM", "Ascending Right", 8.98,4.51 ,30 ;% 12
    "ICEYE", "Ascending Right" , 0.19,0.42 ,30.08 ;% 13
    "ICEYE", "Ascending Right" , 1.45, 0.77, 34.09;% 14
    "ICEYE", "Descending Right" ,  0.18, 0.42, 27.07;% 15
    "ICEYE", "Ascending Right" ,  0.18 ,0.42 ,32.86 ;% 16
    "TSX", "Ascending Right" , 3,1.32,26; % 17
    "TSX", "Descending Right" ,  3.25 , 1.1,21.5 ; % 18
    };


for l = 1:length(toto)
    Sat(l,1)=toto{l,1};
    track=toto{l,2};
    TRACK(l,1:2)=split(track,' ');
    AZ(l,1)=toto{l,3};
    RA(l,1)=toto{l,4};
    INCID(l,1)=toto{l,5};
end


MODE=[char(TRACK(k,1)),' ',char(TRACK(k,2))];
if strcmp(MODE,'Ascending Right') | strcmp(MODE,'Descending Left')
    incid=-INCID(k);
else
    incid=INCID(k);
end
SAT=Sat(k);
azim=AZ(k);
slra=RA(k);

end

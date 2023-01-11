function PlotVolc3D(inputfile,k)
% Matlab function to plot volcano shape in 3D and synthetic radar image 
% Inputs definifion
%inputfile='input_shape.m'; % geometrical parameters of the volcano
%k=5; % raw number for choosing satelite characteristics in the liste define by input_sat.m

% Map footprint in meters
xmin=-3500; xmax=3500;
ymin=-3500; ymax=3500;
ech=501; % x and y sampling number
subs=5; % subsampling intervalle for plots
ech2=1000; % range sampling for amplitude computation

%% Load inputs
[SAT,MODE,incid,azim,slra]=input_sat(k);
run(inputfile);

%% Define grid
x=linspace(xmin,xmax,ech);
y=linspace(ymin,ymax,ech);
[X,Y]=meshgrid(x,y);
Z=zeros(size(X)); %initialise elevation at 0m everywhere

%% Define 3D Volcano
% cone edifice
theta_edifice=atan((Rcald-Rbase)/(Zbase-Zvolc));
ind=find(X.^2+Y.^2<=Rbase^2);
Z(ind)=Rbase/tan(theta_edifice)-sqrt((X(ind).^2+Y(ind).^2)/(tan(theta_edifice))^2);
% inverted cone caldera
theta_cald=atan((R_P2-Rcald)/(Zvolc-ZP2));
ind=find(X.^2+Y.^2<=Rcald^2);
Z(ind)=Zvolc-Zbase+Rcald/tan(theta_cald)+sqrt((X(ind).^2+Y(ind).^2)/(tan(theta_cald))^2);
Z=Z+Zbase;
% Platform P2
ind=find(X.^2+Y.^2<=R_P2^2);
Z(ind)=ZP2;
% Crater cylinder
ind=find((X-decalX).^2+Y.^2<=Rcrat^2);
Z(ind)=Z(ind)-Beta*(ZP2-ZBotcrat);
% crater inverted cone
theta_crat=atan(Rcrat*(Alpha-1)/((ZP2-ZBotcrat)*(1-Beta)));
Z(ind)=Z(ind)+Rcrat/tan(theta_crat)+sqrt(((X(ind)-decalX).^2+Y(ind).^2)/(tan(theta_crat))^2);
% crater flat bottom
ind=find((X-decalX).^2+Y.^2<=(Alpha*Rcrat)^2);
Z(ind)=ZBotcrat;

%% Define objects of interest 
t=linspace(0,360,1000)';
caldera=[Rcald*cos(t),Rcald*sin(t),t*0+Zvolc];
P2=[R_P2*cos(t),R_P2*sin(t),t*0+ZP2];
crat=[Rcrat*cos(t)+decalX,Rcrat*sin(t),t*0+ZP2];
interm=[Rcrat*cos(t)+decalX,Rcrat*sin(t),t*0+ZP2-(ZP2-ZBotcrat)*Beta];
bot=[Alpha*Rcrat*cos(t)+decalX,Alpha*Rcrat*sin(t),t*0+ZBotcrat];
base=[Rbase*cos(t),Rbase*sin(t),t*0+Zbase];

%% Projection 
% projection on Plane z=x*tand(incid)+Zvolc (defined by vectors ey, inciddir and point M(0,0,Zvolc)
inciddir=[sind(incid) 0 cosd(incid)]; % simplified Radar look
M=[0 0 Zvolc];
%project objects
caldera_proj=proj_ortho(caldera,M(3),incid);
P2_proj=proj_ortho(P2,M(3),incid);
crat_proj=proj_ortho(crat,M(3),incid);
interm_proj=proj_ortho(interm,M(3),incid);
bot_proj=proj_ortho(bot,M(3),incid);
base_proj=proj_ortho(base,M(3),incid);

%projection of  some lines of interest  
ind=find(abs(X-decalX)==min(abs(x-decalX)));
proj=proj_ortho([X(ind),Y(ind),Z(ind)],M(3),incid);
ind2=find(abs(X)==min(abs(x)));
proj2=proj_ortho([X(ind2),Y(ind2),Z(ind2)],M(3),incid);

%projection of all points (X,Y,Z)
[n,p]=size(Z);
points2proj=[reshape(X,n*p,1), reshape(Y,n*p,1),reshape(Z,n*p,1)];
pointsproj=proj_ortho(points2proj,M(3),incid);
Xproj=reshape(pointsproj(:,1),n,p);
Yproj=reshape(pointsproj(:,2),n,p);
Zproj=reshape(pointsproj(:,3),n,p);

%% Compute Distances for simulated amplitude
%initialisation
Dist=zeros(size(Z)); 
Distcum=zeros(size(Z));
Distnorm=zeros(size(Z));

for k=2:p
    Dist(:,k)=((Z(:,k)-Z(:,k-1)).^2+(X(:,k)-X(:,k-1)).^2).^0.5; % compute distance topo between two consecutive points for all raws
    Distcum(:,k)=Distcum(:,k-1)+Dist(:,k); % compute cumulative distance since the beginning of the profiles
end
maxdistcum=max(Distcum,2); %compute distance max of each profile

for k=1:n
    Distnorm(k,:)=Dist(k,:)./maxdistcum(k); % normalize Dist with distance max of each profile
end

Vec=[pointsproj-repmat(M,n*p,1)]; %compute vector between each projected point and fixed point M

for k=1:n*p
    distproj(k,:)=dot(Vec(k,:),inciddir); %compute scalar product of Vac with direction of incidence (distance along range)
end
Distproj=reshape(distproj,n,p);
mindistproj=min(min(Distproj));
maxdistproj=max(max(Distproj));

distotprojforinterp=linspace(mindistproj,maxdistproj,ech2)'; %interpole range regular sampling
Matdist=zeros(n,p,ech2);
for k=1:n
    distprojk=Distproj(k,:);
    mindistprojk= min(distprojk);
    maxdistprojk= max(distprojk);
    distotproj=linspace(mindistproj,maxdistproj,ech2)'; 
    for l=2:p
        dist1=distprojk(l-1);
        dist2=distprojk(l);
        if dist1<dist2
            ind=find(distotproj>dist1 & distotproj<=dist2);
        else
            ind=find(distotproj<=dist1 & distotproj>dist2);
        end
        Matdist(k,l,ind)=Distnorm(k,l)/abs(dist1-dist2)*abs(maxdistprojk-mindistprojk);
    end
end
MATDIST(:,:)=sum(Matdist,2); % compute simu ampli


if strcmp(MODE,'Ascending Right') | strcmp(MODE,'Descending Left')
 %MATDIST=fliplr(MATDIST);
 sign=-1;
else
    sign=1
end

%% Plot
figure;
ax(1)=subplot(1,2,1);
hold on;
surf(X(1:subs:end,1:subs:end),Y(1:subs:end,1:subs:end),Z(1:subs:end,1:subs:end),'FaceAlpha',0.1,'EdgeAlpha',0.1)
colormap gray
mesh(Xproj(1:subs:end,1:subs:end),Yproj(1:subs:end,1:subs:end),Zproj(1:subs:end,1:subs:end),'FaceAlpha',0.5,'EdgeAlpha',0.5)
xlabel('X (m)')
ylabel('Y (m)')
zlabel('Z (m)')
plot3(caldera(:,1),caldera(:,2),caldera(:,3),'b')
plot3(P2(:,1),P2(:,2),P2(:,3),'c')
plot3(crat(:,1),crat(:,2),crat(:,3),'r')
plot3(bot(:,1),bot(:,2),bot(:,3),'m')
plot3(base(:,1),base(:,2),base(:,3),'k')
plot3(interm(:,1),interm(:,2),interm(:,3),'Color',[1 0.5 0])
quiver3(0,0,3500,inciddir(1),inciddir(2),inciddir(3),100,'k')
quiver3(0,0,3500,-inciddir(3),inciddir(2),inciddir(1),100,'r')
view([0 -1 0])
title([SAT,' ',MODE,' Incidence',num2str(incid),'°'])
plot3(X(ind),Y(ind),Z(ind),'g')
plot3(X(ind2),Y(ind2),Z(ind2),'k')
xlim([min(x) max(x)])
ylim([min(y) max(y)])
zlim([min(min(Z)) max(max(Z))+100])
axis equal
axis image

ax(2)=subplot(2,2,2);
imagesc(sign*distotprojforinterp/slra,y/azim,MATDIST )
colormap gray
cmean=mean(MATDIST,'all');
caxis([cmean-cmean*80/100 cmean+cmean*200/100])
xlabel('Range (Pixels)')
ylabel('Azimuth (Pixels)')
axis image


ax(3)=subplot(2,2,4);
imagesc(sign*distotprojforinterp/slra,y/azim,MATDIST) %%% PB !!
colormap gray
cmean=mean(MATDIST,'all');
caxis([cmean-cmean*80/100 cmean+cmean*150/100])
 hold on
 plot(caldera_proj(:,1)/abs(sind(incid))/slra,caldera_proj(:,2)/azim,'b')
 plot(P2_proj(:,1)/abs(sind(incid))/slra,P2_proj(:,2)/azim,'c')
 plot(crat_proj(:,1)/abs(sind(incid))/slra,crat_proj(:,2)/azim,'r')
 plot(bot_proj(:,1)/abs(sind(incid))/slra,bot_proj(:,2)/azim,'m')
 plot(interm_proj(:,1)/abs(sind(incid))/slra,interm_proj(:,2)/azim,'Color',[1 0.5 0])
 plot(base_proj(:,1)/abs(sind(incid))/slra,base_proj(:,2)/azim,'k')
 %plot(proj(:,1)/abs(sind(incid))/slra,proj(:,2)/azim,'g')
 %plot(proj2(:,1)/abs(sind(incid))/slra,proj2(:,2)/azim,'k')
xlabel('Range (Pixels)')
ylabel('Azimuth (Pixels)')
axis image
axis normal
end

%%%%%%%%%%% SUBFUNCTIONS%%%%%%%%%%ùù
function proj=proj_ortho(points,z0,incid)
% compute orthogonal projection of point [x,y,z] along plane defined by
% inciddir, ey and M[0,0,z0]
% incidence angle in degree
u=sind(incid); w=cosd(incid);
proj=[(points(:,1)+(points(:,3)-z0)*w/u)/(1+(w/u)^2), points(:,2), (points(:,1)+z0*u/w+points(:,3)*w/u)/(u/w+w/u)];
end
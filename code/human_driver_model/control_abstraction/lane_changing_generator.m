% LANE_CHANING_GENERATOR - File that generates the table of a passing and returning to 
% the initial lane.

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 16-Apr-2018; Last revision: 12-May-2018

%------------- BEGIN CODE --------------

clc
warning('off','all')

% Car size for collision purposes (both cars are assumed to be of equal dimensions)
h = 1.9;
w = 4.8;

% Possible initial distances between the vehicles
ds = linspace(1,43,43);
% ds = 25;

% Possible vehicles initial velocity
vi1s = linspace(15,34,20);
vi2s = linspace(15,34,20);
% vi1s = 30;
% vi2s = 20;

% Road width/length + time intervals for action
global width len delta_t
width = 7.4;
len = 500;
delta_t = 0.5;
n_iter = 100;

% Code starts

generated_table = zeros(2*length(ds)*length(vi1s)*length(vi2s), 9);
display(sprintf('Generating table of %d entries', size(generated_table,1)))
t1 = cputime;

other_table = zeros(2*length(ds)*length(vi1s)*length(vi2s), 14);

textprogressbar('Progress: ')

% Simulate all possible combinations
for lane = 2:-1:1
for vi2_i = 1:length(vi2s)
    for vi1_i = 1:length(vi1s)
        for d_i = 1:length(ds)
            
            d = ds(d_i);
            vi1 = vi1s(vi1_i);
            vi2 = vi2s(vi2_i);
            
            sum_x = 0;
            sum_vx = 0;
            sum_t = 0;
            sum_col = 0;
            
            x_y_t = zeros(13*n_iter,3);
            
%             f = figure(1);
%             hold on;
            
            for j=1:n_iter
                
                if lane == 1
                    x = d;
                else
                    x = 0;
                end
                y = (-2*lane + 5)*width/4;
                vx = vi1;
                vy = 0;

                if lane == 1
                    x1 = 0;
                else
                    x1 = d;
                end
                y1 = width/4;
                vx1 = vi2;
                vy1 = 0;

                old_theta_near = 0;
                old_theta_far = 0;
                old_thw_car = (x1 - x)/vx;

                vehicles_pos = [x1,y1];

                col = false;
                t = 0;
                ay = 100;

                x_y_t(13*(j - 1) + 1,:) = [0,x,y];
                idx_sub = 2;

                while x < len && ~(abs(y - (2*lane-1)*width/4) < 0.02)
                    col = check_collision([x,y], vehicles_pos, h, w) || col;

                    [x,y,vx,vy,ay,old_theta_near,old_theta_far,old_thw_car] = control(x,y,vx,vy,lane,old_theta_near,old_theta_far,old_thw_car,vehicles_pos);

                    vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                    vehicles_pos(1,2) = vehicles_pos(1,2) + vy1*delta_t;

                    t = t + delta_t;

                    x_y_t(13*(j - 1) + idx_sub,:) = [t, x, y];
                    idx_sub = idx_sub + 1;

%                     plot(vehicles_pos(1,1), vehicles_pos(1,2), 'or')
                end

                while floor(t) ~= t
                    x = x + vx*delta_t;
                    vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                    t = t + delta_t;

                    x_y_t(13*(j - 1) + idx_sub,:) = [t, x, y];
                    idx_sub = idx_sub + 1;
%                     plot(vehicles_pos(1,1), vehicles_pos(1,2), 'or')
                end
                
%                 sum_x = sum_x + x;
                sum_vx = sum_vx + vx;
                sum_t = sum_t + t;
                sum_col = sum_col + col;
            end
            
            if lane == 1
                sub_mat = d*[zeros(size(x_y_t,1), 1), ones(size(x_y_t,1),1), zeros(size(x_y_t,1), 1)];
                x_y_t = x_y_t - sub_mat;
            end
            
            p_x = polyfit(x_y_t(:,1),x_y_t(:,2),2);
            p_y = polyfit(x_y_t(:,1),x_y_t(:,3),6);
            
%             plot(x_y_t(:,2), x_y_t(:,3),'ob')
%             p_xy = polyfit(x_y_t(:,2),x_y_t(:,3),5);
%             x1 = linspace(0,max(x_y_t(:,2)));
%             y1 = polyval(p_xy,x1);
%             plot(x1,y1)
%             axis([0,max(x1),0,max(y1)])
            
%             est_x1 = round(sum_x/n_iter)
            est_vx = round(sum_vx/n_iter);
            est_t = round(sum_t/n_iter);
            est_x = round(polyval(p_x,est_t));
            est_col = sum_col/n_iter;
                                    
            idx = (2-lane)*length(ds)*length(vi1s)*length(vi2s) + (vi2_i - 1)*length(vi1s)*length(ds) + (vi1_i - 1)*length(ds) + d_i;
            
%             generated_table(idx,:) = [3-lane,d,vi1,vi2,col,round(x - (d)*(2-lane)),round(vx),round(vehicles_pos(1,1)-(d)*(lane-1)),t];
            generated_table(idx,:) = [3-lane,d,vi1,vi2,est_col,round(est_x - (d)*(2-lane)),est_vx,round(vi2*est_t-(d)*(lane-1)),est_t];
            other_table(idx,:) = [3-lane,d,vi1,vi2,p_x,p_y];
            
            textprogressbar(100*idx/(2*length(ds)*length(vi1s)*length(vi2s)))
        end
    end
end
end

textprogressbar('Done')

display(sprintf('Generated in %.3f seconds', cputime - t1))

% Display the table
header = {'o_lane','d','vi1','vi2','Acc?','delta_x1','vf1','delta_x2','delta_t'};
xForDisplay = [header; num2cell(generated_table)];
% disp(xForDisplay)

header_1 = {'o_lane','d','vi1','vi2','p_x(1)','p_x(2)','p_x(3)','p_y(1)','p_y(2)','p_y(3)','p_y(4)','p_y(5)','p_y(6)','p_y(7)'};
xForDisplay = [header_1; num2cell(other_table)];
% disp(xForDisplay)

% Save the table generated to a CSV file with a header
cHeader = header;
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen(sprintf('data/gen_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vi1s(1), vi1s(length(vi1s)), vi2s(1), vi2s(length(vi2s))),'w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite(sprintf('data/gen_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vi1s(1), vi1s(length(vi1s)), vi2s(1), vi2s(length(vi2s))),generated_table,'-append');

% Save the other table as well
cHeader = header_1;
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen('data/other_table.csv','w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite('data/other_table.csv',other_table,'-append');

%------------- END OF CODE --------------
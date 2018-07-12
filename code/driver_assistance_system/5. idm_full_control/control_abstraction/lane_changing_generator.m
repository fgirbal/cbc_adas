% LANE_CHANING_GENERATOR - File that generates the table of a passing and returning to 
% the initial lane.

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 11-Jul-2018; Last revision: 11-Jul-2018

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

set_k = [15, 3, 5; 17, 3, 6; 14.5, 3, 7];

% Road width/length + time intervals for action
global width len delta_t
width = 7.4;
len = 500;
delta_t = 0.5;
n_iter = 100;

% Code starts

n_entries = 2*length(ds)*length(vi1s)*length(vi2s)*size(set_k,1);
generated_table = zeros(n_entries, 9);
display(sprintf('Generating table of %d entries', size(generated_table,1)))
t1 = cputime;

other_table = zeros(2*length(ds)*length(vi1s)*length(vi2s)*size(set_k,1), 24);

textprogressbar('Progress: ')

% Simulate all possible combinations
for lane = 2:-1:1
for vi2_i = 1:length(vi2s)
    for vi1_i = 1:length(vi1s)
        for d_i = 1:length(ds)
        for i = 1:size(set_k,1)
            
            d = ds(d_i);
            vi1 = vi1s(vi1_i);
            vi2 = vi2s(vi2_i);

            k_far = set_k(i,1);
            k_near = set_k(i,2);
            k_i = set_k(i,3);
            
            sum_x = 0;
            sum_vx = 0;
            sum_t = 0;
            sum_col = 0;
            
%             f = figure(1);
%             hold on;

            x_y_t = [];
            bad_run_example = [];
                        
            for j=1:n_iter
                
                x = (2 - lane)*d;
                y = (-2*lane + 5)*width/4;
                vx = vi1;
                vy = 0;

                x1 = (lane - 1)*d;
                y1 = width/4;
                vx1 = vi2;
                vy1 = 0;

                old_theta_near = 0;
                old_theta_far = 0;
                old_thw_car = (x1 - x)/vx;

                vehicles_pos = [x1,y1];

                col = false;
                t = 0;
                ay = 0;

                temp = [];
                temp(1,:) = [0,x,y];
                idx_sub = 2;
                
                while x < len && ~(abs(y - (2*lane-1)*width/4) < 0.02)
                    col = check_collision([x,y], vehicles_pos, h, w) || col;
                    
                    [x,y,vx,vy,ay,old_theta_near,old_theta_far,old_thw_car] = control(x,y,vx,vy,lane,old_theta_near,old_theta_far,old_thw_car,vehicles_pos,k_far,k_near,k_i);

                    vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                    vehicles_pos(1,2) = vehicles_pos(1,2) + vy1*delta_t;

                    t = t + delta_t;

                    temp(idx_sub,:) = [t, x, y];
                    idx_sub = idx_sub + 1;

%                     plot(vehicles_pos(1,1), vehicles_pos(1,2), 'or')
                end

                while floor(t) ~= t
                    x = x + vx*delta_t;
                    vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                    t = t + delta_t;

                    temp(idx_sub,:) = [t, x, y];
                    idx_sub = idx_sub + 1;
%                     plot(vehicles_pos(1,1), vehicles_pos(1,2), 'or')
                end
                
%                 sum_x = sum_x + x;
                sum_vx = sum_vx + vx;
                sum_t = sum_t + t;
                sum_col = sum_col + col;
                                
                if col == 0
                    x_y_t = [x_y_t; temp];
                else
                    bad_run_example = temp;
                end
            end
            
            if lane == 1
                if size(x_y_t,1) ~= 0
                    sub_mat = d*[zeros(size(x_y_t,1), 1), ones(size(x_y_t,1),1), zeros(size(x_y_t,1), 1)];
                    x_y_t = x_y_t - sub_mat;
                end
                
                if size(bad_run_example,1) ~= 0
                    other_sub_mat = d*[zeros(size(bad_run_example,1), 1), ones(size(bad_run_example,1),1), zeros(size(bad_run_example,1), 1)];
                    bad_run_example = bad_run_example - other_sub_mat;
                end
            end
            
            if size(x_y_t,1) == 0
                x_y_t = [0,0,0];
            end
            
            if sum_col/n_iter == 0
                bad_run_example = [0,0,0];
            end
                                    
            p_x = polyfit(x_y_t(:,1),x_y_t(:,2),2);
            p_y = polyfit(x_y_t(:,1),x_y_t(:,3),6);
            
            bad_p_x = polyfit(bad_run_example(:,1),bad_run_example(:,2),2);
            bad_p_y = polyfit(bad_run_example(:,1),bad_run_example(:,3),6);
            
%             plot(x_y_t(:,2), x_y_t(:,3),'ob')
%             plot(bad_run_example(:,2), bad_run_example(:,3),'*r')
%             p_xy = polyfit(x_y_t(:,2),x_y_t(:,3),5);
%             bad_p_xy = polyfit(bad_run_example(:,2),bad_run_example(:,3),5);
%             x1 = linspace(0,max(x_y_t(:,2)));
%             y1 = polyval(p_xy,x1);
%             plot(x1,y1,'b')
%             x1 = linspace(0,max(bad_run_example(:,2)));
%             y1 = polyval(bad_p_xy,x1);
%             plot(x1,y1,'r')
%             
%             pause
            
%             est_x1 = round(sum_x/n_iter)
            est_vx = max(round(sum_vx/n_iter), vi1);
            est_t = round(sum_t/n_iter);
            est_x = round(polyval(p_x,est_t));
            est_col = sum_col/n_iter;
                                    
            idx = (2-lane)*length(ds)*length(vi1s)*length(vi2s)*size(set_k,1) + (vi2_i - 1)*length(vi1s)*length(ds)*size(set_k,1) + (vi1_i - 1)*length(ds)*size(set_k,1) + (d_i - 1)*size(set_k,1) + i;
            
            generated_table(idx,:) = [3-lane,d,vi1,vi2,est_col,round(est_x - (d)*(2-lane)),est_vx,round(vi2*est_t-(d)*(lane-1)),est_t];
            other_table(idx,:) = [3-lane,d,vi1,vi2,p_x,p_y,bad_p_x,bad_p_y];
            
            textprogressbar(100*idx/n_entries)
        end
        end
    end
end
end

textprogressbar('Done')

display(sprintf('Generated in %.3f seconds', cputime - t1))

% Display the table
header = {'o_lane','d','vi1','vi2','Acc?','delta_x1','vf1','delta_x2','delta_t'};
% xForDisplay = [header; num2cell(generated_table)];
% disp(xForDisplay)

header_1 = {'o_lane','d','vi1','vi2','p_x(1)','p_x(2)','p_x(3)','p_y(1)','p_y(2)','p_y(3)','p_y(4)','p_y(5)','p_y(6)','p_y(7)','bad_p_x(1)','bad_p_x(2)','bad_p_x(3)','bad_p_y(1)','bad_p_y(2)','bad_p_y(3)','bad_p_y(4)','bad_p_y(5)','bad_p_y(6)','bad_p_y(7)'};
% xForDisplay = [header_1; num2cell(other_table)];
% disp(xForDisplay)

% Save the table generated to a CSV file with a header
cHeader = header;
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen('data/control_table.csv','w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite('data/control_table.csv',generated_table,'-append');

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
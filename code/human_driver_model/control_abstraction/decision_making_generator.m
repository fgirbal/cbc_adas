% DECISION_MAKING_GENERATOR - File that generates the decision making table
% in terms of probability of changing lanes at certain points

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 24-Apr-2018; Last revision: 24-Apr-2018

%------------- BEGIN CODE --------------

clc

% Possible initial distances between the vehicles
ds = linspace(1,10,10);

% Possible vehicle initial velocity
vs = linspace(15,34,20);

generated_table = zeros(2*length(ds)*length(vs), 9);
display(sprintf('Generating table of %d entries', size(generated_table,1)))
t1 = cputime;

% Simulate all possible combinations
for lane = 1:2
    for v_i = 1:length(vs)
        for d_i = 1:length(ds)
            
            d = ds(d_i);
            vi1 = vs(v_i);
            vi2 = vi2s(vi2_i);
            
            if lane == 1
                x = w + d;
            else
                x = 0;
            end
            y = (-2*lane + 5)*width/4;
            vx = vi1;
            vy = 0;

            if lane == 1
                x1 = 0;
            else
                x1 = w + d;
            end
            y1 = width/4;
            vx1 = vi2;
            vy1 = 0;

            old_theta_near = 0;
            old_theta_far = 0;
            old_thw_car = (x1 - x)/vx;

            vehicles_pos = [x1,y1];

%             f = figure(1);
%             hold on;
%             axis([0,len,0,width])

            col = false;
            t = 0;
            ay = 100;

            while x < len && ~(abs(ay) < 0.01 && abs(y - (2*lane-1)*width/4) < 0.05)
                [x,y,vx,vy,ay,old_theta_near,old_theta_far,old_thw_car] = control(x,y,vx,vy,lane,old_theta_near,old_theta_far,old_thw_car,vehicles_pos);
                
%                 plot(x, y, 'ob')

                vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                vehicles_pos(1,2) = vehicles_pos(1,2) + vy1*delta_t;

%                 plot(vehicles_pos(1,1), vehicles_pos(1,2), 'or')

                col = check_collision([x,y], vehicles_pos, h, w) || col;
                t = t + delta_t;
%                 pause
            end
            
            while floor(t) ~= t
                x = x + vx*delta_t;
                vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
                t = t + delta_t;
            end
            
            idx = (2-lane)*length(ds)*length(vs)*length(vi2s) + (vi2_i - 1)*length(vs)*length(ds) + (v_i - 1)*length(ds) + d_i;
         
            generated_table(idx,:) = [3-lane,d,vi1,vi2,col,round(x - (w + d)*(2-lane)),round(vx),round(vehicles_pos(1,1)-(w + d)*(lane-1)),t];
        end
    end
end
end

display(sprintf('Generated in %.3f seconds', cputime - t1))

% Display the table
header = {'o_lane','d','vi1','vi2','Acc?','delta_x1','vf1','delta_x2','delta_t'};
xForDisplay = [header; num2cell(generated_table)];
disp(xForDisplay)

% Save the table generated to a CSV file with a header
cHeader = header;
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen(sprintf('data/gen_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vs(1), vs(length(vs)), vi2s(1), vi2s(length(vi2s))),'w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite(sprintf('data/gen_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vs(1), vs(length(vs)), vi2s(1), vi2s(length(vi2s))),generated_table,'-append');

%------------- END OF CODE --------------
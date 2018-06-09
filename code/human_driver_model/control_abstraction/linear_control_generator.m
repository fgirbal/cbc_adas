% LINEAR_ACCELARATION_GENERATOR - File that generates the accelaration
% table based on the time headway of the car.

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 24-Apr-2018; Last revision: 6-Jun-2018

%------------- BEGIN CODE --------------

clc

% Possible initial distances between the vehicles
ds = linspace(1,80,80);

% Possible vehicle initial velocity
vs = linspace(15,34,20);

generated_table = zeros(length(ds)*length(vs), 4);
display(sprintf('Generating table of %d entries', size(generated_table,1)))
t1 = cputime;

for d_i = 1:length(ds)
    for v_i = 1:length(vs)

        d = ds(d_i);
        v = vs(v_i);

        delta_crash = d/v;

%         if delta_crash < 0.3
%             a = -1;
%         elseif delta_crash <= 1
%             a = 0;
%         else
%             a = 1;
%         end

        if delta_crash <= 0.2
            a = -2;
        elseif delta_crash <= 0.4
            a = -1;
        elseif delta_crash <= 1
            a = 0;
        elseif delta_crash <= 1.75
            a = 1;
        elseif delta_crash <= 2.5
            a = 2;
        else
            a = 3;
        end
        
        idx = (d_i - 1)*length(vs) + v_i;

        generated_table(idx,:) = [d,v,round(delta_crash,2),a];
    end
end

display(sprintf('Generated in %.3f seconds', cputime - t1))

% Display the table
header = {'d','v','delta_crash','a'};
xForDisplay = [header; num2cell(generated_table)];
disp(xForDisplay)

% Save the table generated to a CSV file with a header
cHeader = header;
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
textHeader = textHeader(1:end-1);

%write header to file
fid = fopen('data/mod_acceleration_table.csv','w'); 
fprintf(fid,'%s\n',textHeader);
fclose(fid);

%write data to end of file
dlmwrite('data/mod_acceleration_table.csv',generated_table,'-append');

%------------- END OF CODE --------------
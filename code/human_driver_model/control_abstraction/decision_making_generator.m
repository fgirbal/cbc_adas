% DECISION_MAKING_GENERATOR - File that generates the decision making table
% in terms of probability of changing lanes at certain points

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 24-Apr-2018; Last revision: 24-Apr-2018

%------------- BEGIN CODE --------------

clc

% Possible initial distances between the vehicles
ds = linspace(1,80,80);

% Possible vehicle initial velocity
vs = linspace(15,34,20);

generated_table = zeros(length(ds)*length(vs), 6);
display(sprintf('Generating table of %d entries', size(generated_table,1)))
t1 = cputime;

% Simulate all possible combinations
for d_i = 1:length(ds)
    for v_i = 1:length(vs)
        
        d = ds(d_i);
        v = vs(v_i);
        
        delta_crash = d/v;
        
        idx = (d_i - 1)*length(vs) + v_i;
        
        generated_table(idx,:) = [d,v,delta_crash,0,0,0];
    end
end

display(sprintf('Generated in %.3f seconds', cputime - t1))

% Display the table
header = {'d','v','delta_crash','P_lC','P_dec','P_no_action'};
xForDisplay = [header; num2cell(generated_table)];
disp(xForDisplay)

% Save the table generated to a CSV file with a header
% cHeader = header;
% commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commaas
% commaHeader = commaHeader(:)';
% textHeader = cell2mat(commaHeader); %cHeader in text with commas
% textHeader = textHeader(1:end-1);
% 
% %write header to file
% fid = fopen(sprintf('data/dm_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vs(1), vs(length(vs)), vi2s(1), vi2s(length(vi2s))),'w'); 
% fprintf(fid,'%s\n',textHeader);
% fclose(fid);
% 
% %write data to end of file
% dlmwrite(sprintf('data/dm_table_%d_%d_%d_%d_%d_%d.csv', ds(1), ds(length(ds)),vs(1), vs(length(vs)), vi2s(1), vi2s(length(vi2s))),generated_table,'-append');

%------------- END OF CODE --------------
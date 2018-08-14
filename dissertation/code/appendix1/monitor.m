function [ monitoring_memory ] = monitor( monitoring_memory,x,vehicles_pos )
%MONITOR ACT-R monitor module

global pMonitor width length;

if rand > pMonitor
    return
end

% Look vehicle
pm = rand;
if pm < 0.25
    lane_dir = 1; % lane 1, back
    
    min_dist = length+1;
    for i = 1:size(vehicles_pos,1)
        if vehicles_pos(i,1) < x && abs(vehicles_pos(i,2) - width/4) < 0.2
            d = abs(vehicles_pos(i,1) - x);
            min_dist = min(min_dist, d);
        end
    end
    if min_dist == length+1
        exists = false;
    else
        exists = true;
    end
    new_info = [lane_dir, exists, min_dist];
    
elseif pm < 0.5
    lane_dir = 2; % lane 1, front
    
    min_dist = length+1;
    for i = 1:size(vehicles_pos,1)
        if vehicles_pos(i,1) > x && abs(vehicles_pos(i,2) - width/4) < 0.2
            d = abs(vehicles_pos(i,1) - x);
            min_dist = min(min_dist, d);
        end
    end
    if min_dist == length+1
        exists = false;
    else
        exists = true;
    end
    new_info = [lane_dir, exists, min_dist];
    
elseif pm < 0.75
    lane_dir = 3; % lane 2, back
    
    min_dist = length+1;
    for i = 1:size(vehicles_pos,1)
        if vehicles_pos(i,1) < x && abs(vehicles_pos(i,2) - 3*width/4) < 0.2
            d = abs(vehicles_pos(i,1) - x);
            min_dist = min(min_dist, d);
        end
    end
    if min_dist == length+1
        exists = false;
    else
        exists = true;
    end
    new_info = [lane_dir, exists, min_dist];
    
else
    lane_dir = 4; % lane 2, front
    
    min_dist = length+1;
    for i = 1:size(vehicles_pos,1)
        if vehicles_pos(i,1) > x && abs(vehicles_pos(i,2) - 3*width/4) < 0.2
            d = abs(vehicles_pos(i,1) - x);
            min_dist = min(min_dist, d);
        end
    end
    if min_dist == length+1
        exists = false;
    else
        exists = true;
    end
    new_info = [lane_dir, exists, min_dist];
end

% Add to memory
monitoring_memory = [monitoring_memory(2:size(monitoring_memory,1),:); new_info];

end


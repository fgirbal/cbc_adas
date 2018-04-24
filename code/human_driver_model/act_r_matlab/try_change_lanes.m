function [ lane, changing ] = try_change_lanes( destination, dec_memory, vehicles_pos, x )
%TRY_CHANGE_LANES Function part of the decision making ACT-R module

global width length;

% Constant
d_safe = 50;

if destination == 1
    dest_lane = width/4;
    mems = [1, 2];
else
    dest_lane = 3*width/4;
    mems = [3, 4];
end

% Check memory for vehicles
closest = Inf;
for i = 1:size(dec_memory,1)
    if ismember(dec_memory(i,1), mems) && dec_memory(i,2) == 1 && dec_memory(i,3) < closest
        closest = dec_memory(i,3);
    end
end

if closest < d_safe
    lane = 3 - destination; % stay in the same lane
    changing = false;
    return
end

% Check vehicle for vehicle in front
min_dist = length+1;
for i = 1:size(vehicles_pos,1)
    if vehicles_pos(i,1) > x && abs(vehicles_pos(i,2) - dest_lane) < 0.2
        d = abs(vehicles_pos(i,1) - x);
        min_dist = min(min_dist, d);
    end
end

if min_dist < d_safe && min_dist ~= length+1
    lane = 3 - destination; % stay in the same lane
    changing = false;
    return
end

% Check vehicle for vehicle behind
min_dist = length+1;
for i = 1:size(vehicles_pos,1)
    if vehicles_pos(i,1) < x && abs(vehicles_pos(i,2) - dest_lane) < 0.2
        d = abs(vehicles_pos(i,1) - x);
        min_dist = min(min_dist, d);
    end
end

if min_dist < d_safe && min_dist ~= length+1
    lane = 3 - destination; % stay in the same lane
    changing = false;
    return
end

% Checked memory, did double-verification and no vehicle in sight, so switch lane
lane = destination;
changing = true;

end


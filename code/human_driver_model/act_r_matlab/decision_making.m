function [ lane, changing ] = decision_making( lane, old_thw_car, x, y, dec_memory, changing, vehicles_pos )
%DECISION_MAKING ACT-R decision making module

global width;

% Constant
thw_pass = 20;

% Check whether a lane change is happening or not
if changing == true
    if lane == 1 && abs(y - width/4) < 0.1
        changing = false;
    elseif lane == 2 && abs(y - 3*width/4) < 0.1
        changing = false;
    end
    
    return
end

if old_thw_car < thw_pass && lane == 1
    % attempt to change lanes
    [lane,changing] = try_change_lanes(2, dec_memory, vehicles_pos, x);
    if changing == 1
        abs(x - vehicles_pos(1,1))
        pause
    end
elseif old_thw_car < thw_pass && lane == 2
    % attempt to change lanes
    [lane,changing] = try_change_lanes(1, dec_memory, vehicles_pos, x);
    if changing == 1
        abs(x - vehicles_pos(2,1))
        pause
    end
end

end


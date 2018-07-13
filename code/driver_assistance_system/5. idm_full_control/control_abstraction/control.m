function [x,y,vx,vy,ay,old_theta_near,old_theta_far,old_thw_car] = control( x, y, vx, vy, lane, old_theta_near, old_theta_far, old_thw_car, vehicles_pos, k_far, k_near, k_i )
%CONTROL ACT-R control module

global delta_t width;

% Constants
% k_far = 15;%15;
% k_near = 3;%3;
% k_i = 5;%5;
theta_nmax = 1.57;
k_car = 3;%4;
k_follow = 1;
max_speed = 34; % approximately 120 km/h

std_dev = 0;

if lane == 1
    y_follow = width/4;
else
    y_follow = 3*width/4;
end

near_point = [x + 4, y_follow];
far_point = [x + 10, y_follow];

theta_near = tan((near_point(2) - y)/(near_point(1) - x));
theta_far = tan((far_point(2) - y)/(far_point(1) - x));

Delta_theta_near = theta_near - old_theta_near;
Delta_theta_far = theta_far - old_theta_far;

Delta_varphi = k_far*Delta_theta_far + k_near*Delta_theta_near + k_i*min(theta_near,theta_nmax)*delta_t;

% To determine timeheadway, check for vehicles/accidents between the
% car position and far point; the timeheadway corresponds to the
% timeheadway to the closest vehicle (or the end of the road)

min_timeheadway = 3 + normrnd(0,std_dev); % the maximum timeheadway
for i = 1:size(vehicles_pos,1)
    if vehicles_pos(i,1) > x && abs(vehicles_pos(i,2) - y) < 0.2
        th = (vehicles_pos(i,1) - x + normrnd(0,std_dev))/vx;
        min_timeheadway = min(min_timeheadway, th);
    end
end
time_headway = min_timeheadway;

Delta_time_headway = time_headway - old_thw_car;

Delta_psi = k_car*Delta_time_headway + k_follow*(time_headway - 1)*delta_t;

ax = Delta_psi;
if Delta_varphi ~= 0
    ay = sin(Delta_varphi);
else
    ay = 0;
end

% Update variables

if vx + ax*delta_t < max_speed
    vx = vx + ax*delta_t;
end
vy = vy + ay*delta_t;

x = x + vx*delta_t + 0.5*ax*delta_t^2;
y = y + vy*delta_t + 0.5*ay*delta_t^2;

old_theta_near = theta_near;
old_theta_far = theta_far;
old_thw_car = time_headway;

end


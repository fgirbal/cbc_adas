% TEST_CONTROLLERS - Obtain plots of several controllers.

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

d = 20;
vi1 = 15;
vi2 = 15;
lane = 2;

global width len delta_t
width = 7.4;
len = 500;
delta_t = 0.5;

sum_x = 0;
sum_vx = 0;
sum_t = 0;
sum_col = 0;

set_k = [15, 3, 5; 17, 3, 6; 14.5, 3, 7];
color_array = [1,0,0;0,1,0;0,0,1];

f = figure(1);
hold on

for i = 1:size(set_k,1)

    k_far = set_k(i,1);
    k_near = set_k(i,2);
    k_i = set_k(i,3);

    x_y_t = [];

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

    x_y_t = temp;

    if lane == 1
        sub_mat = d*[zeros(size(x_y_t,1), 1), ones(size(x_y_t,1),1), zeros(size(x_y_t,1), 1)];
        x_y_t = x_y_t - sub_mat;
    end

    p_x = polyfit(x_y_t(:,1),x_y_t(:,2),2);
    p_y = polyfit(x_y_t(:,1),x_y_t(:,3),6);

    c = color_array(i,:);

    plot(x_y_t(:,2), x_y_t(:,3),'o','color',c,'HandleVisibility','off')
    hold on
%                 plot(bad_run_example(:,2), bad_run_example(:,3),'*r')
    p_xy = polyfit(x_y_t(:,2),x_y_t(:,3),5);
    x1 = linspace(0,max(x_y_t(:,2)));
    y1 = polyval(p_xy,x1);
    plot(x_y_t(:,2), x_y_t(:,3),'color',c,'DisplayName',sprintf('k_f=%.1f, k_n=%.1f, k_i=%.1f',k_far,k_near,k_i))
    hold on
end

plot([0,200], [(-2*1 + 5)*width/4,(-2*1 + 5)*width/4], 'color',[0.1,0.1,0.1],'HandleVisibility','off')
plot([0,200], [(-2*2 + 5)*width/4,(-2*2 + 5)*width/4], 'color',[0.1,0.1,0.1],'HandleVisibility','off')
plot([0,200], [width/2,width/2], 'color',[0.5,0.5,0.5],'HandleVisibility','off')

hold off
legend('show', 'location', 'Southeast');


%------------- END OF CODE --------------
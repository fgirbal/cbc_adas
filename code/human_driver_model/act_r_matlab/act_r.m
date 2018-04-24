% ACT_R - Matlab implementation of Salvucci's human driver model using the
% cognitive architecture ACT-R.

% Author: Francisco Girbal Eiras, MSc Computer Science
% University of Oxford, Department of Computer Science
% Email: francisco.eiras@cs.ox.ac.uk
% 07-Mar-2018; Last revision: 24-Apr-2018

%------------- BEGIN CODE --------------

figure('pos',[300 300 800 350])
g = animatedline('Color','g','LineWidth',3);
h = animatedline('Color','r','LineWidth',3);

% Draw the separating line

global delta_t length width mem_size pMonitor;
length = 10000; % 10km
width = 7.2;
delta_t = 1;
mem_size = 8;
pMonitor = 0.8;

hold on
plot([0, length], [width/2, width/2], '--k');
plot([0, length], [width/4, width/4], '--b');
plot([0, length], [3*width/4, 3*width/4], '--g');

% Draw the car in the other line

axis([0 length 0 width])

% Vehicle info
x = 0;
y = width/4;
lane = 1;
vx = 15;
vy = 0;

% Obstacles info
x1 = 50;
y1 = width/4;
vx1 = 34;
vy1 = 0;

x2 = 5500;
y2 = 3*width/4;

vehicles_pos = [x1,y1; x2,y2];

% Memory preparation
old_theta_near = 0;
old_theta_far = 0;
old_thw_car = (x1 - x)/vx;

% Graph preparation
ll = plot(x2, y2, 'sk', 'MarkerSize', 14, 'MarkerFaceColor','black');
hold off
lh = legend([g h ll], sprintf('vx = %.2d, vy = %.2f', vx, vy), sprintf('vx = %.2d, vy = %.2f', vx1, vy1), 'Time: ');

changing = false;
t = 0;
monitoring_memory = zeros(mem_size,3);

while x < length
    
    [x,y,vx,vy,old_theta_near,old_theta_far,old_thw_car] = control(x,y,vx,vy,lane,old_theta_near,old_theta_far,old_thw_car,vehicles_pos);
    
    monitoring_memory = monitor(monitoring_memory,x,vehicles_pos)
    
    [lane, changing] = decision_making(lane, old_thw_car, x, y, monitoring_memory, changing, vehicles_pos);
    
    % Other car
    vehicles_pos(1,1) = vehicles_pos(1,1) + vx1*delta_t;
    vehicles_pos(1,2) = vehicles_pos(1,2) + vy1*delta_t;
    
    % Graphical visualisation
    addpoints(g,x,y);
    addpoints(h,vehicles_pos(1,1),vehicles_pos(1,2));
    
    set(lh, 'string', {sprintf('vx = %.2f, vy = %.2f', vx, vy), sprintf('vx = %.2f, vy = %.2f', vx1, vy1),sprintf('Time: %.0f s', t)});
    
    drawnow
    
    t = t + delta_t;
end

%------------- END OF CODE --------------
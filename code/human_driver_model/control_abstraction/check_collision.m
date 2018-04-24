function happened = check_collision( vehicle_1, vehicle_2, h, w )
%CHECK_COLLISION Verify the occurence of a collision

rect_1 = [vehicle_1(1) - w/2, vehicle_1(2) + h/2, w, h];
rect_2 = [vehicle_2(1) - w/2, vehicle_2(2) + h/2, w, h];

area = rectint(rect_1, rect_2);

happened = (area ~= 0);

end


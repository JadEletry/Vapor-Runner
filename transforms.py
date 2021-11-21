# Before updating the vertical lines we want to transform the coordinates
# From the 2D display to create a perspective plane

# We can call the transform_2D function to display the 2D plane
# # We will call our perpective function for the game at the end
def transform(self, x, y):
    # return self, self.transform_2D(x, y)
    return self.transform_perspective(x, y)
    
def transform_2D(self, x, y):
    return int(x), int(y)
    
# When the height is the size of the display
# We transofrm y from the 2D plane to be the height of the perspective point y
 # The perspective point is constant for all transformations greater than it
def transform_perspective(self, x, y):
    linear_y = y * self.perspective_point_y / self.height 
    if linear_y > self.perspective_point_y:
         linear_y = self.perspective_point_y
    
# When changning the display size, we resize our perspective lines accordingly
# x is greater than the perspective point, y is less than 
# # The more we approach the perspective point, 
# The more the proportion decreases
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - linear_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = pow(factor_y, 4) # We can change the attraction rate between our horizontal lines
        
    trans_x = self.perspective_point_x + diff_x * factor_y
    trans_y = self.perspective_point_y - factor_y * self.perspective_point_y
        
    return int(trans_x), int(trans_y)
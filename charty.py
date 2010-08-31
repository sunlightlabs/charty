
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import math
from nice import nice_ticks_seq

CURRENCY = [( 10**3, 'Th'), (10**6, 'M'), (10**9, 'B'), (10**12, 'Tr')]


class Chart(object):
    """Base class for SVG chart generation
       Data is expected in a list of lists, with (x,y) tuples:
            [ [(1, 2),(2, 3), ..], [...] ]
       
       or with labels instead of x values:
    
            [ [('risk transfers', 300), ('loans', 200), ..], ... ] 

    """
    def __init__(self, width, height, data, stylesheet=None, **kwargs):
        
        self.height = height
        self.width = width
        self.data = data
        self.numeric_labels = False
        self.number_of_series = len(data)
        self.labels = self.extract_labels()
        self.label_rotate = 0
        self.stylesheet = stylesheet
        self.padding = 30
        self.x_padding = 0
        self.y_padding = 0
        self.currency = False
        self.units = ''

 
        #create svg node as root element in tree
        self.svg = ET.Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1", height=str(self.height), width=str(self.width) )
        self.svg.attrib["xmlns:svg"] = "http://www.w3.org/2000/svg"
         
        #there really isn't a graceful way for loading an external stylesheet when you're not in a browser so we parse it in and spit it out inside style tags
        temp = []
        stylesheet = open(self.stylesheet, 'r')
        for x in stylesheet.readlines():
            temp.append(x)
        self.svg.append(ET.XML('<style type="text/css">' + "\n".join(temp)  + '</style>'))

    def find_y_minimum(self):
        min_y_value = None

        for series in self.data:
            #Because series are incrementally numbered, we allow for a place holder to keep styles consistent
            if series != 'placeholder':
                for point in series:
                    if not min_y_value or (not isinstance(point[1], "".__class__) and point[1] < min_y_value): min_y_value = point[1]

        return min_y_value

    def find_y_maximum(self):
        """
            Function to find the maximum x and y values of all series 
            as well as the maximum number of points in a given series
        """
        max_y_value = 0

        for series in self.data:
            #Because series are incrementally numbered, we allow for a place holder to keep styles consistent
            if series != 'placeholder':
                for point in series:
                    if not isinstance(point[1], "".__class__) and point[1] > max_y_value: max_y_value = point[1]

        return max_y_value

    def are_labels_numeric(self, labels):
        numeric = True
        for l in labels:
            if isinstance(l, type("")):
                numeric = False
                break
        if numeric:
            self.numeric_labels = True
            return [x for x in range(min(labels), max(labels)+1)]
        else: return labels

    def extract_labels(self):
        """
            Pull out the distinct labels from each data series
        """ 
        labels = []
        self.numeric_labels = True
        for series in self.data:
            if series != 'placeholder':
                for point in series:
                    if isinstance(point[0], str): self.numeric_labels = False
                    if not point[0] in labels: labels.append(point[0])

        return self.are_labels_numeric(labels)
            
    def output(self, write_file):
        """
            Output the svg xml tree as text
        """
        #DEBUG - Dump properties
        #for x in self.__dict__.keys():
            #pass#print "%s : %s\n" % (x, self.__dict__[x]) 
        txt = ET.tostring(self.svg)
        f = open(write_file, 'w')
        f.write(parseString(txt).toprettyxml() )
   
class Pie(Chart):
    """Subclass of Chart, containing functions relevant to all pie charts"""

    def __init__(self, height, width, data, stylesheet=None, **kwargs):

        super(Pie, self).__init__(height, width, data, stylesheet, **kwargs)
        #Catch passed in keyword argument overrides of defaults
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
             
        #find sum of values, only needed for pie charts
        self.total = 0
        for series in self.data:
            for point in series:
                self.total += point[1]

        if (self.width - (2 * self.x_padding)) > (self.height - (2 * self.y_padding)):
            self.diameter = self.height - (2 * self.y_padding) - (2 * self.padding)
        else:
            self.diameter = self.width - (2 * self.x_padding) - (2 * self.padding)
        
        self.radius = self.diameter / 2
        self.x_origin = self.radius + self.x_padding + self.padding
        self.y_origin = self.radius + self.y_padding + self.padding
        self.svg.append(ET.Element("rect", x="0", y="0", height="%s" % self.height, width="%s" % self.width, fill="white"))  # attach stage
        
        self.data_series() #Chart subclass should have this method to chart the data series

    
    def data_series(self):
        """ Process data and draw pie slices """

        total_angle = 0
        count = 1
        last_point = [self.radius, 0]
        arc = 0 #draw the short arc by default
        for series in self.data:
            for point in series:
                angle = (point[1] / float(self.total)) * 360
                total_angle += angle
                
                if angle > 180:
                    arc = 1  #draw the long arc
                else: arc = 0
                percent = (point[1] / float(self.total)) * 100
                if math.floor(percent) == percent: percent = int(percent)
                point1 = "M %s,%s " % (self.x_origin, self.y_origin)
                point2 = "l %s,%s " % (last_point[0], -last_point[1])

                x = math.cos(math.radians(total_angle)) * self.radius
                y = math.sin(math.radians(total_angle)) * self.radius
              
                total_label_angle = total_angle - (angle / 2)

                x_label = (math.cos(math.radians(total_label_angle)) * self.radius) + self.x_origin 
                y_label = self.y_origin - int(math.sin(math.radians(total_label_angle)) * self.radius)
                
                if x_label > (self.x_origin + 24): x_label += 7  #some rough adjustments to the label for edge cases
                elif x_label < (self.x_origin - 24): x_label -= 7

                if y_label > (self.y_origin + 12): y_label += 10  #check and see if it's within 12 pixels of the 180 line, avg font height
                elif y_label < (self.y_origin - 12): y_label -= 10

                point3 = "a%s,%s 0 %s,0 %s,%s z" % (self.radius, self.radius, arc, (x - last_point[0]), -(y - last_point[1]))
                              
                self.add_label(x_label, y_label, point[0], percent) 
                last_point = [x, y]
                path = ET.Element("path", d="%s %s %s" % (point1, point2, point3))
                path.attrib['class'] = 'slice-%s' % count
                self.svg.append(path)
                count += 1
   
    def add_label(self, x, y, label_text, percent):

        label = ET.Element("text", x="%d" % x, y="%d" % y)
        if x < self.x_origin:
            label.attrib['class'] = 'pie-label-left'
        else:
            label.attrib['class'] = 'pie-label-right'
        
        if isinstance(percent, float): pct_text = "%0.1f" % percent + "%" + " - "
        else: pct_text = "%g" % percent + "%" + " - "
        
        lines = str(label_text).split("\n")
        height = (len(lines) - 1) * 15
        label.y = y + height

        for l in lines:
            elem = ET.Element("tspan", dy="15", x="%s" % x)
            if l == lines[0]:
                elem.text = pct_text + l 
                elem.attrib['dy'] = "0"
            else:
                elem.text = l
            label.append(elem)

        self.svg.append(label)
    
class GridChart(Chart):
    """Subclass of Chart, containing functions relevant to all charts that use a grid"""
    def __init__(self, height, width, data, stylesheet=None, *args, **kwargs):

        self.gridline_percent = .10
        self.x_label_height = 15  #insert a check for multi line labels on x axis
        self.x_label_padding = 15
        self.y_label_padding = 5
        self.y_label_height = 15
        self.label_intervals = 1
        
        super(GridChart, self).__init__(height, width, data, stylesheet, **kwargs)
        #Catch passed in keyword argument overrides of defaults
        for key in kwargs:
            self.__dict__[key] = kwargs[key] 

        #set the baseline coordinates of the actual grid
        self.grid_y1_position = self.padding
        self.grid_y2_position = self.height - self.x_label_height - self.padding - self.y_padding
        self.grid_x1_position = self.padding + self.x_padding
        self.grid_x2_position = self.width - self.padding - self.x_padding
        self.grid_height = self.grid_y2_position - self.grid_y1_position
        self.grid_width = self.grid_x2_position - self.grid_x1_position

        #where and how often for gridlines
        self.max_y_value =  self.find_y_maximum()      
        if hasattr(self, 'use_zero_minimum') and self.use_zero_minimum:
            self.min_y_value = 0
        else:
            self.min_y_value = self.find_y_minimum()

        self.max_x_value = max(self.labels)
        self.max_data_points = len(self.labels)
        if not hasattr(self, 'gridlines'):
            self.gridlines = 5
        
        print self.min_y_value
        print self.max_y_value 
        self.gridline_values = nice_ticks_seq(self.min_y_value, self.max_y_value, self.gridlines, False)
        print self.gridline_values
        self.gridlines = len(self.gridline_values) - 1
        self.min_y_axis_value = min(self.gridline_values)
        self.max_y_axis_value = max(self.gridline_values)
        self.y_scale = self.grid_height / float(self.max_y_axis_value)
        self.y_display_unit = self.get_display_unit()
        

    def setup_chart(self):

        #setup background color
        self.svg.append(ET.Element("rect", x="0", y="0", height="%s" % self.height, width="%s" % self.width, fill="white"))
        self.grid = ET.Element("g", id="grid", transform="translate(%s, %s)" % (self.grid_x1_position, self.grid_y1_position))
        self.svg.append(self.grid)

        #add x and y axes
        x_axis, y_axis = [ET.Element("g", id="x_axis"), ET.Element("g", id="y_axis")]
        x_axis.attrib['class'], y_axis.attrib['class'] = ['x-axis', 'y-axis']

        x_axis_path = ET.Element("path", d="M %d %d L %d %d" % (0, self.grid_height, self.grid_width, self.grid_height))
        x_axis_path.attrib['class'] = 'x-axis-path'

        x_axis.append(x_axis_path)

        y_axis_path = ET.Element("path", d="M %d %d L %d %d" % (0, self.grid_height, 0, 0))
        y_axis_path.attrib['class'] = 'y-axis-path'
        
        notch1 = ET.Element("path", d="M %d %d, L %d %d" % (0, self.grid_height, 0, self.grid_height + 10))
        notch2 = ET.Element("path", d="M %d %d, L %d %d" % (self.grid_width, self.grid_height, self.grid_width, self.grid_height + 10))
        notch1.attrib['class'] = 'x-notch-left'
        notch2.attrib['class'] = 'x-notch-right'
        x_axis.append(notch1)
        x_axis.append(notch2)
        y_axis.append(y_axis_path)
        
        y_axis_path2 = ET.Element("path", d="M %d %d L %d %d" % (self.grid_width, self.grid_height, self.grid_width, 0))    
        y_axis_path2.attrib['class'] = 'y-axis-path-2'
        y_axis.append(y_axis_path2)

        grid_space = self.grid_height / self.gridlines
        grid_value_increment = self.max_y_axis_value / self.gridlines
         
        count = 0
        for label in self.gridline_values:
            #draw the gridline
            gridline = ET.Element("path", d="M %d %d L %d %d" % (0, (self.grid_height - count * grid_space), self.grid_width, (self.grid_height - count * grid_space)))
            gridline.attrib['class'] = 'y-gridline'
            y_axis.append(gridline)

            #draw the text label
            gridline_label = ET.Element("text", x="%s" % (-self.y_label_padding), y="%s" % ( self.grid_height - (count * grid_space) ) )
            #um = self.max_y_axis_value - (count * grid_value_increment)
            text = "%s" % label
            text = self.convert_units(label)

            gridline_label.text = text
            gridline_label.attrib['class'] = 'y-axis-label'
            y_axis.append(gridline_label)
            count += 1

        self.grid.append(x_axis)
        self.grid.append(y_axis)

    def check_label_types(self):

        current_type = type(self.labels[0])
       # for label in self.labels:
        #START HERE    

    def data_point_label(self, value, x, y):
        dp_label = ET.Element("text", x="%s" % x, y="%s" % y)
        text = str(value)
        text = self.convert_units(value)
        dp_label.text = "%s" % text
        dp_label.attrib['class'] = 'data-point-label'
        self.grid.append(dp_label)

    def get_display_unit(self):
#need to change this to be for tick marks, not actual data points
        if self.min_y_axis_value != 0:
            print self.min_y_axis_value
            return self.match_unit(self.min_y_axis_value)
        else:
            return self.match_unit(self.gridline_values[1])

            min_unit = (1000000000000, 'Tr')
            for series in self.data:
                if series != 'placeholder':
                    for point in series:
                        temp_unit = self.match_unit(point[1])
                        if temp_unit[0] < min_unit[0]:
                            min_unit = temp_unit
                            break

            return min_unit

    def match_unit(self, value):
        for unit in reversed(CURRENCY):
            if value / float(unit[0]) >= 1:
                return unit

        return (1, '')
                    
    def convert_units(self, value):
        text = ""
        if self.currency:
            text = "$"
        text = text + "%2g" % round (value / self.y_display_unit[0], 2)
        if self.units:
            text = text + self.y_display_unit[1]
        return text

class Line(GridChart):

    def __init__(self, height, width, data, stylesheet=None, *args, **kwargs):

        super(Line, self).__init__(height, width, data, stylesheet, **kwargs)
       
        self.x_scale = self.set_scale()  #find the width of each point in each series
        self.x_group_scale = self.x_scale * self.number_of_series  #width of each data point grouping over multiple series
        self.setup_chart()

        self.data_series()  #Chart subclass should have this method to chart the data series
        #self.labels.sort() # Yikes! sorting the labels independently from the data leads to problems... 
        self.set_labels()
         
    def set_scale(self):
        #pixels between data points
        return float(self.grid_width - (self.x_padding * 2) ) / (len(self.labels) - 1) 

    def data_series(self):
        
        series_count = 0
        left_offset = self.padding  
        bottom_offset = self.padding
        g_container = ET.Element('g')
        
        for series in self.data:
            series_count += 1
            if series != 'placeholder':
                #move path to initial data point
                data_point_count = self.labels.index(series[0][0])
                path_string = "M %s %s" % (self.x_padding + int(data_point_count * self.x_scale), self.grid_height - (series[0][1] * self.y_scale))

                for point in series:
                    if data_point_count == 0: 
                        data_point_count += 1
                        continue

                    data_point_count = self.labels.index(point[0]) 
                    path_string += " L "
                    x = self.x_padding + int(data_point_count * self.x_scale)
                    point_height = self.y_scale * point[1]                
                    y = self.grid_height - point_height
                    path_string += "%s %s" % (x, y)
                    data_point_count += 1
                    #put point markers in here at some point?

                line = ET.Element("path", d=path_string)
                line.attrib['class'] = 'series-%s-line' % series_count
                g_container.append(line)
        self.grid.append(g_container)
    
    def set_labels(self):

        label_count = 0

        for l in self.labels:
            if  (self.label_intervals and label_count % self.label_intervals == 0) or not self.label_intervals:
                text_item = ET.Element("text")
                x_position = self.x_padding + (label_count * self.x_scale)
                y_position = self.grid_height + self.x_label_padding
                text_item.attrib['x'] = "%s" % x_position
                text_item.attrib['y'] = "%s" % y_position
                text_item.text = "%s" % l
                text_item.attrib['class'] = 'x-axis-label'
                self.grid.append(text_item)
                
                #insert the notch between data point groups
                if l != self.labels[-1]:
                    if self.label_intervals:
                        skip_labels = self.label_intervals
                    else: skip_labels = 1

                    notch_x_pos = x_position + (((self.x_padding + ((label_count + skip_labels) * self.x_scale)) - x_position) / 2)
                    notch_y_pos = self.grid_height
                    notch = ET.Element("path", d="M %s %s L %s %s" % (notch_x_pos, notch_y_pos, notch_x_pos, notch_y_pos + 5))
                    notch.attrib['class'] = 'x-notch'
                    self.grid.append(notch)
            label_count += 1

class Column(GridChart):
    """Subclass of GridChart class, specific to an n-series column chart """
    
    def __init__(self, height, width, data, stylesheet=None, *args, **kwargs):

        super(Column, self).__init__(height, width, data, stylesheet, **kwargs)

        self.max_x_point_width = 60  #How wide should a bar chart be if there's plenty of white space -->move to bar chart only

        #find the width of each point in each series
        self.x_scale = self.set_scale()
        
        #width of each data point grouping over multiple series
        self.x_group_scale = self.x_scale * self.number_of_series
        self.setup_chart()

        #Chart subclass should have this method to chart the data series
        self.data_series()
        #self.labels.sort() # Yikes! sorting the labels independently from the data leads to problems... 
        self.set_labels()
         

    def set_scale(self):
        
        scale = (self.grid_width / self.max_data_points / self.number_of_series)# - self.x_padding
        if self.max_x_point_width < scale:
            #need to adjust white space padding
            self.x_padding = (self.grid_width - (self.number_of_series * self.max_data_points * self.max_x_point_width)) / (self.max_data_points)
            return self.max_x_point_width
        else:
            return scale

    def data_series(self):

        series_count = 0
        left_offset = self.padding  
        bottom_offset = self.padding
        
        for series in self.data:
            data_point_count = 0
            for point in series:
                data_point_count = self.labels.index(point[0])
                point_width = self.x_scale
                x_position = (self.x_padding / 2) + (data_point_count * (self.x_group_scale + self.x_padding) ) + (series_count * point_width)

                if isinstance(point[1], (int, long, float, complex)):
                    point_height = self.y_scale * point[1]
                else:
                    #value may be a string to display
                    point_height = self.max_y_axis_value * self.y_scale
                    text = ET.Element("text", x="%s" % x_position, y="%s" % (self.grid_height - (point_height/2)))
                    words = point[1].split(' ')
                    num_words = 0
                    for w in words:
                        text_span = ET.Element("tspan", x="%s" % x_position, y="%s" % (self.grid_height - ((len(words) * 14) - (num_words * 14) ) ))  
                        text_span.text = w
                        text.append(text_span)
                        num_words += 1

                    text.attrib['class'] = 'value-as-label'
                    self.grid.append(text)
                    data_point_count += 1
                    continue
                
                y_position = (self.grid_height - point_height)
                data_point = ET.Element("rect", x="%s" % x_position, y="%s" % y_position, height="%s" % point_height, width="%s" % point_width  )
                data_point.attrib['class'] = 'series-%s-point' % series_count

                #insert the notch between data point groups
                if series == self.data[-1] and point != series[-1]:
                    notch_x_pos = x_position + (point_width) + (self.x_padding / 2)
                    notch_y_pos = self.grid_height
                    notch = ET.Element("path", d="M %s %s L %s %s" % (notch_x_pos, notch_y_pos, notch_x_pos, notch_y_pos + 5))
                    notch.attrib['class'] = 'x-notch'
                    self.grid.append(notch)
            
                self.grid.append(data_point)
                self.data_point_label(point[1], x_position + (point_width / 2), y_position - 5)
                data_point_count += 1

            series_count += 1


    def add_label(self, label, label_count, word_count=0):
            x_position = int((self.x_padding / 2) + (self.x_group_scale / 2) + (label_count * (self.x_group_scale + self.x_padding)))
            y_position = self.grid_height + self.x_label_padding + (13 * word_count)
            text_item = ET.Element("text", x="%s" % x_position, y="%s" % y_position)
            text_item.text = "%s" % label
            text_item.attrib['class'] = 'x-axis-label'
            if self.label_rotate:
                text_item.attrib['transform'] = "rotate(%s, %s, %s)" % (self.label_rotate, x_position, y_position)
                if self.label_rotate < 1:
                    text_item.attrib['style'] = "text-anchor: end;"
                else:
                    text_item.attrib['style'] = 'text-anchor: start;'
            self.grid.append(text_item)

    def set_labels(self):
        label_count = 0
        for l in self.labels:
            if not self.numeric_labels:
                if len(l.split('\n')):
                    #multiline label
                    word_count = 0
                    for word in l.split('\n'):
                        self.add_label(word, label_count, word_count)
                        word_count += 1
                else:
                    self.add_label(l, label_count)
            else:
                self.add_label(l, label_count)

            label_count += 1

% Function to make figures more visually appealing

% Define function
function formatfigure(figure_handle,plot_width,plot_height,margin)

% Specify line width, font size, tick length
line_width = 1;
box_line_width = 0.5;
font_size = 7;
tick_length = 1;

% Set figure size
figure_width = margin+plot_width+margin;
figure_height = margin+plot_height+margin;
set(figure_handle,'units','centimeters','position', ...
    [0 0 figure_width figure_height]);

% Set axis size
axis_handle = gca(figure_handle);
set(axis_handle,'Units','centimeters');
set(axis_handle,'Position',[margin margin plot_width plot_height]);

% Make sure font sizes are correct
axis_handle.TitleFontSizeMultiplier = 1;
axis_handle.LabelFontSizeMultiplier = 1;

% Get axis handle and set font
set(axis_handle,'FontName','Helvetica','FontSize',font_size);
box(axis_handle,'on');
axis_handle.TickLength(1) = 0.1*tick_length/max(axis_handle.Position(3:4));
axis_handle.TickLength(2) = 0.1*tick_length/max(axis_handle.Position(3:4));

% Change width of data lines
axis_lines = findobj(axis_handle,'Type','line');
set(axis_lines,'LineWidth',line_width);

% Set the box line width
axis_handle.LineWidth = box_line_width;

% Ensure the figure is displayed correctly
drawnow;
end

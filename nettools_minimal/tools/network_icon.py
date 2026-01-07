"""
Network Icon Generator
Creates custom network topology icons for the application
"""

from PIL import Image, ImageDraw


class NetworkIcon:
    """Generate custom network icon"""
    
    @staticmethod
    def create_icon(size=256):
        """Create network topology icon"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Colors
        fg_color = (80, 80, 80)
        bg_color = (235, 235, 235)
        device_color = (210, 210, 210)
        
        # Main router/switch box
        pad = int(size * 0.12)
        box_size = size - 2 * pad
        corner = int(box_size * 0.15)
        
        # Draw rounded rectangle for main device
        draw.rounded_rectangle(
            [pad, pad, pad + box_size, pad + box_size],
            radius=corner,
            fill=bg_color,
            outline=fg_color,
            width=3
        )
        
        # Draw monitor/screen on top
        monitor_w = int(box_size * 0.65)
        monitor_h = int(box_size * 0.32)
        mx = pad + (box_size - monitor_w) // 2
        my = pad + 2
        draw.rectangle([mx, my, mx + monitor_w, my + monitor_h], 
                      fill=device_color, outline=fg_color, width=2)
        
        # Draw stand
        stand_h = int(box_size * 0.08)
        sx = mx + (monitor_w - stand_h) // 2
        sy = my + monitor_h + 2
        draw.rectangle([sx, sy, sx + stand_h, sy + stand_h], fill=fg_color)
        
        # Draw vertical line from stand
        line_x = sx + stand_h // 2
        line_y1 = sy + stand_h
        line_y2 = line_y1 + 12
        draw.line([line_x, line_y1, line_x, line_y2], fill=fg_color, width=3)
        
        # Draw connected devices (3 squares)
        sq_size = int(box_size * 0.18)
        gap = int(box_size * 0.06)
        total_width = 3 * sq_size + 2 * gap
        start_x = line_x - total_width // 2
        sq_y = line_y2 + 10
        
        for i in range(3):
            x = start_x + i * (sq_size + gap)
            # Draw device square
            draw.rectangle([x, sq_y, x + sq_size, sq_y + sq_size],
                          fill=device_color, outline=fg_color, width=2)
            
            # Draw connection line from device to hub
            center_x = x + sq_size // 2
            draw.line([center_x, sq_y, center_x, sq_y - 10], 
                     fill=fg_color, width=2)
            draw.line([line_x, line_y2 + 1, center_x, sq_y - 10],
                     fill=fg_color, width=2)
        
        return img

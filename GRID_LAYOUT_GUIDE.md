# Live Ping Monitor - Grid Layout Guide

## Overview
The Live Ping Monitor now uses an efficient **grid layout** to display multiple hosts side-by-side, allowing you to monitor more hosts at once in a compact, organized view.

## Grid Layout Features

### Configurable Columns
Choose from:
- **2 Columns** (Default) - Best for detailed viewing
- **3 Columns** - Balanced view for 6-12 hosts
- **4 Columns** - Maximum density for 12+ hosts

### Layout Comparison

#### 2 Column Layout (Default)
```
┌─────────────────┬─────────────────┐
│   Host 1        │   Host 2        │
│   [Graph]       │   [Graph]       │
├─────────────────┼─────────────────┤
│   Host 3        │   Host 4        │
│   [Graph]       │   [Graph]       │
└─────────────────┴─────────────────┘
```

#### 3 Column Layout
```
┌───────────┬───────────┬───────────┐
│  Host 1   │  Host 2   │  Host 3   │
│  [Graph]  │  [Graph]  │  [Graph]  │
├───────────┼───────────┼───────────┤
│  Host 4   │  Host 5   │  Host 6   │
│  [Graph]  │  [Graph]  │  [Graph]  │
└───────────┴───────────┴───────────┘
```

#### 4 Column Layout
```
┌────────┬────────┬────────┬────────┐
│ Host 1 │ Host 2 │ Host 3 │ Host 4 │
│[Graph] │[Graph] │[Graph] │[Graph] │
├────────┼────────┼────────┼────────┤
│ Host 5 │ Host 6 │ Host 7 │ Host 8 │
│[Graph] │[Graph] │[Graph] │[Graph] │
└────────┴────────┴────────┴────────┘
```

## Host Card Components

Each grid cell contains:

```
┌─────────────────────────────────┐
│ ● 192.168.1.1                   │  ← Status dot + IP
│   (router.local)                │  ← Hostname (if available)
│ Avg: 12ms  Loss: 0%  Pings: 45 │  ← Live statistics
│ ┌───────────────────────────┐   │
│ │                           │   │
│ │     [Latency Graph]       │   │  ← Real-time graph
│ │                           │   │
│ └───────────────────────────┘   │
└─────────────────────────────────┘
```

### Status Indicator Colors
- 🟢 **Green**: Online, good latency (<50ms)
- 🟡 **Yellow**: Online, high latency (≥50ms)
- 🔴 **Red**: Offline/unreachable

### Statistics Display
- **Avg**: Average latency in milliseconds
- **Loss**: Packet loss percentage
- **Pings**: Total number of pings sent

### Graph Features
- **X-axis**: Last 30 pings
- **Y-axis**: Latency in milliseconds (auto-scaling)
- **Line**: Green line with markers showing each ping
- **Grid**: Light grid for easier reading
- **Compact**: Optimized size for grid layout

## Using the Grid Layout

### 1. Start Monitoring
1. Enter hosts in the input field
2. Select desired grid layout (2/3/4 columns)
3. Click "▶ Start Monitoring"

### 2. Change Layout During Monitoring
- Use the **Grid Layout** dropdown to change columns
- Layout reorganizes automatically
- No interruption to monitoring

### 3. Best Practices

**For 2-6 hosts:**
- Use **2 Columns** for larger graphs and easier reading
- Best for detailed monitoring

**For 6-12 hosts:**
- Use **3 Columns** for balanced view
- Good compromise between detail and density

**For 12+ hosts:**
- Use **4 Columns** for maximum screen utilization
- Best for overview monitoring

## Window Size

The Live Monitor window opens at **1100x750 pixels**, optimized for:
- Clear visibility in 2-column mode
- Adequate space for graphs
- Easy scanning of multiple hosts
- Modern monitor resolutions (1920x1080+)

## Responsive Design

### Grid automatically adjusts:
- **Column weights**: Each column gets equal width
- **Row expansion**: New rows added as needed
- **Scrolling**: Vertical scroll for many hosts
- **Reorganization**: Instant when changing layout

## Performance Considerations

### Recommended Limits
- **2 Columns**: Up to 20 hosts
- **3 Columns**: Up to 30 hosts  
- **4 Columns**: Up to 40 hosts

### Beyond Recommendations
- More hosts are possible but may slow UI updates
- Consider multiple monitor windows instead
- Or increase update interval (currently 1 second)

## Graph Optimization

The graphs in grid mode are optimized:
- **Smaller figure size**: 4x1.8 inches (vs 8x2 in vertical)
- **Lower DPI**: 70 (vs 80 in vertical)
- **Compact labels**: Smaller fonts (7pt vs 9pt)
- **Tight layout**: Minimal padding
- **Markers**: Small dots on line for clarity

## Tips for Best Experience

### Viewing Many Hosts
1. Start with 3-column layout
2. Adjust to 2 or 4 columns based on preference
3. Use full-screen mode (F11 in most systems)

### Comparing Hosts
1. Place related hosts in same row
2. Watch for status color changes
3. Compare average latencies at a glance

### Long-term Monitoring
1. Start in 2-column mode for detail
2. Export data periodically
3. Watch for trends in graphs

### Quick Overview
1. Use 4-column layout
2. Focus on status dots and averages
3. Drill down to specific hosts as needed

## Keyboard & Mouse

### Window Controls
- **Resize**: Drag window edges (grid adapts)
- **Scroll**: Mouse wheel or scrollbar
- **Close**: X button or Alt+F4

### No Grid Interaction
- Graphs are read-only displays
- Click buttons for controls
- No drag-and-drop (yet)

## Future Enhancements

Potential improvements:
- Adjustable update interval
- Click host to expand/detail view
- Drag to reorder hosts
- Save layout preferences
- Custom color themes
- Export individual host graphs
- Zoom in/out on graphs

## Technical Details

### Grid Implementation
- Uses tkinter grid geometry manager
- Sticky "nsew" for full cell expansion
- Equal column weights for balanced width
- Dynamic row addition
- Reorganization without recreation

### Update Efficiency
- All hosts update simultaneously
- Canvas redraws only changed data
- Matplotlib figure caching
- No flicker or lag

### Memory Usage
- Each host ~2MB (graph + data)
- 10 hosts ~20MB
- Scales linearly
- 30-ping history limit keeps it constant

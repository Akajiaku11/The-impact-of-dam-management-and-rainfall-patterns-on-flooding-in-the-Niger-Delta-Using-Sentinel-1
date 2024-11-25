var aoi = ee.Geometry.Polygon([
  [
    [3.03125, 4.5],
    [8.03125, 4.5],
    [8.03125, 7.5],
    [3.03125, 7.5],
    [3.03125, 4.5]
  ]
]);
// Define the time period for analysis
var startDate = '2022-09-20';
var endDate = '2022-10-28';

// Load Sentinel-1 SAR dataset
var sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD')
                  .filterBounds(aoi)
                  .filterDate(startDate, endDate)
                  .filter(ee.Filter.eq('instrumentMode', 'IW'))
                  .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
                  .filter(ee.Filter.eq('resolution_meters', 10))
                  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
                  .select('VV');

// Create a median composite image for the period
var medianImage = sentinel1.median().clip(aoi);

// Threshold to identify flood areas (adjust the threshold value based on your AOI)
var floodThreshold = -11;
var floodedArea = medianImage.lt(floodThreshold).selfMask();
var nonFloodedArea = medianImage.gte(floodThreshold).selfMask();

// Display the results
Map.centerObject(aoi, 10);
Map.addLayer(floodedArea, {palette: ['red'], min: 0, max: 1}, 'Flooded Area');
Map.addLayer(nonFloodedArea, {palette: ['blue'], min: 0, max: 1}, 'Non-Flooded Area');

// Calculate flood area statistics
var floodArea = floodedArea.multiply(ee.Image.pixelArea()).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 10,
  maxPixels: 1e10
});

var nonFloodArea = nonFloodedArea.multiply(ee.Image.pixelArea()).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: aoi,
  scale: 10,
  maxPixels: 1e10
});

// Print the results
print('Flooded Area (m^2): ', floodArea.get('VV'));
print('Non-Flooded Area (m^2): ', nonFloodArea.get('VV'));

// Create a chart to visualize the flood and non-flood areas
var chart = ui.Chart.array.values({
  array: [floodArea.get('VV'), nonFloodArea.get('VV')],
  axis: 0
})
.setChartType('PieChart')
.setOptions({
  title: 'Flood vs Non-Flood Areas',
  slices: [{color: 'red'}, {color: 'blue'}],
  labels: ['Flooded Area', 'Non-Flooded Area']
});

print(chart);

// Export the flooded area as a TIFF file
Export.image.toDrive({
  image: floodedArea,
  description: 'FloodedArea_TIFF',
  scale: 10,
  region: floodedArea.geometry().bounds(),
  maxPixels: 1e8,
  fileFormat: 'GeoTIFF'
});

// Export the non-flooded area as a TIFF file
Export.image.toDrive({
  image: nonFloodedArea,
  description: 'NonFloodedArea_TIFF',
  scale: 10,
  region: nonFloodedArea.geometry().bounds(),
  maxPixels: 1e8,
  fileFormat: 'GeoTIFF'
});


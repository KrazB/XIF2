/**
 * Simple IFC File Diagnostic - Analyze large IFC files
 */

const fs = require('fs');
const path = require('path');

function analyzeIfcFile(filePath) {
  console.log(`\n=== IFC FILE ANALYSIS ===`);
  console.log(`File: ${path.basename(filePath)}`);
  
  if (!fs.existsSync(filePath)) {
    console.error(`❌ File not found: ${filePath}`);
    return;
  }
  
  const stats = fs.statSync(filePath);
  const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
  const fileSizeGB = (stats.size / (1024 * 1024 * 1024)).toFixed(3);
  
  console.log(`Size: ${fileSizeMB} MB (${fileSizeGB} GB)`);
  console.log(`Created: ${stats.mtime.toISOString()}`);
  
  // Read first 1MB to analyze structure
  console.log(`\n[ANALYZING] Reading first 1MB for structure analysis...`);
  
  const fd = fs.openSync(filePath, 'r');
  const sampleSize = 1024 * 1024; // 1MB
  const buffer = Buffer.alloc(sampleSize);
  
  try {
    const bytesRead = fs.readSync(fd, buffer, 0, sampleSize, 0);
    fs.closeSync(fd);
    
    const sampleText = buffer.slice(0, bytesRead).toString('utf8');
    
    // Extract header info
    console.log(`\n[HEADER]`);
    const headerMatch = sampleText.match(/FILE_DESCRIPTION\s*\(\s*\((.*?)\)/s);
    const schemaMatch = sampleText.match(/FILE_SCHEMA\s*\(\s*\((.*?)\)/s);
    
    if (headerMatch) {
      console.log(`Description: ${headerMatch[1].replace(/'/g, '').trim()}`);
    }
    if (schemaMatch) {
      console.log(`Schema: ${schemaMatch[1].replace(/'/g, '').trim()}`);
    }
    
    // Count entities in sample
    console.log(`\n[ENTITIES]`);
    const entityMatches = sampleText.match(/#\d+\s*=\s*IFC\w+/g) || [];
    const entityCounts = {};
    
    entityMatches.forEach(match => {
      const entityType = match.match(/IFC\w+/)[0];
      entityCounts[entityType] = (entityCounts[entityType] || 0) + 1;
    });
    
    const sampleRatio = bytesRead / stats.size;
    const estimatedTotal = Math.round(entityMatches.length / sampleRatio);
    
    console.log(`Sample entities: ${entityMatches.length} (${(sampleRatio * 100).toFixed(2)}% of file)`);
    console.log(`Estimated total: ${estimatedTotal.toLocaleString()}`);
    
    // Show top entity types
    console.log(`\n[TOP ENTITY TYPES]`);
    const sorted = Object.entries(entityCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8);
    
    sorted.forEach(([type, count]) => {
      const estimated = Math.round(count / sampleRatio);
      console.log(`  ${type}: ${count} (est. ${estimated.toLocaleString()})`);
    });
    
    // Look for geometry indicators
    console.log(`\n[GEOMETRY COMPLEXITY]`);
    const polyLoops = (sampleText.match(/IFCPOLYLOOP/g) || []).length;
    const cartesianPoints = (sampleText.match(/IFCCARTESIANPOINT/g) || []).length;
    const triangulated = (sampleText.match(/IFCTRIANGULATEDFACESET/g) || []).length;
    const faceSet = (sampleText.match(/IFCFACETEDBREP/g) || []).length;
    
    console.log(`  PolyLoops: ${polyLoops} (est. ${Math.round(polyLoops / sampleRatio).toLocaleString()})`);
    console.log(`  CartesianPoints: ${cartesianPoints} (est. ${Math.round(cartesianPoints / sampleRatio).toLocaleString()})`);
    console.log(`  TriangulatedFaceSets: ${triangulated} (est. ${Math.round(triangulated / sampleRatio).toLocaleString()})`);
    console.log(`  FacetedBreps: ${faceSet} (est. ${Math.round(faceSet / sampleRatio).toLocaleString()})`);
    
    // Processing recommendations
    console.log(`\n[PROCESSING ASSESSMENT]`);
    
    let complexity = 'Medium';
    let memoryEstimate = fileSizeMB * 4;
    let recommendations = [];
    
    if (fileSizeMB > 3000) {
      complexity = 'EXTREME';
      memoryEstimate = fileSizeMB * 8;
      recommendations.push('⚠️  File exceeds 3GB - use preprocessing');
      recommendations.push('💾 Estimated memory needed: 24-32GB');
      recommendations.push('🔧 Strip non-essential entities before conversion');
      recommendations.push('⚡ Consider file splitting or chunked processing');
    } else if (fileSizeMB > 1000) {
      complexity = 'Very High';
      memoryEstimate = fileSizeMB * 6;
      recommendations.push('⚠️  Large file - use enhanced processing');
      recommendations.push('💾 Estimated memory needed: 6-12GB');
      recommendations.push('🔧 Consider preprocessing to reduce size');
    }
    
    if (estimatedTotal > 10000000) {
      recommendations.push(`📊 Very high entity count (${estimatedTotal.toLocaleString()}) - may cause timeouts`);
    }
    
    if (triangulated > 100) {
      recommendations.push('🔺 Complex triangulated meshes detected - high memory usage');
    }
    
    // Check for long lines (huge meshes)
    const lines = sampleText.split('\n');
    const longLines = lines.filter(line => line.length > 10000);
    if (longLines.length > 0) {
      recommendations.push(`🔍 ${longLines.length} extremely long lines detected - possible huge mesh data`);
    }
    
    console.log(`Complexity: ${complexity}`);
    console.log(`Memory estimate: ${Math.round(memoryEstimate)} MB`);
    
    if (recommendations.length > 0) {
      console.log(`\n[RECOMMENDATIONS]`);
      recommendations.forEach(rec => console.log(`  ${rec}`));
    }
    
    // Processing strategy
    console.log(`\n[SUGGESTED STRATEGY]`);
    if (fileSizeMB > 3000) {
      console.log(`1. Use large file processor with preprocessing`);
      console.log(`2. Strip annotations, grids, spaces, zones`);
      console.log(`3. Filter oversized meshes`);
      console.log(`4. Use 16+ GB memory allocation`);
      console.log(`5. Consider chunked processing if still fails`);
    } else if (fileSizeMB > 1000) {
      console.log(`1. Use enhanced memory-optimized converter`);
      console.log(`2. Allocate 8-16GB memory`);
      console.log(`3. Enable garbage collection`);
      console.log(`4. Use streaming with chunked reading`);
    } else {
      console.log(`1. Standard converter should work`);
      console.log(`2. Use 4-8GB memory allocation`);
    }
    
  } catch (error) {
    fs.closeSync(fd);
    console.error(`❌ Analysis error:`, error.message);
  }
}

// Command line execution
const args = process.argv.slice(2);
if (args.length < 1) {
  console.log('Usage: node diagnose_ifc.js <input.ifc>');
  process.exit(1);
}

const inputFile = path.resolve(args[0]);
analyzeIfcFile(inputFile);

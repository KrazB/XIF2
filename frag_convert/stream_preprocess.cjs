/**
 * Streaming IFC Preprocessor - Handle massive files without loading into memory
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

async function streamPreprocessIfc(inputPath, outputPath) {
  console.log(`\n=== STREAMING IFC PREPROCESSOR ===`);
  console.log(`Input: ${path.basename(inputPath)}`);
  console.log(`Output: ${path.basename(outputPath)}`);
  
  if (!fs.existsSync(inputPath)) {
    console.error(`❌ Input file not found: ${inputPath}`);
    return false;
  }
  
  const startTime = Date.now();
  const stats = fs.statSync(inputPath);
  const inputSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
  
  console.log(`Original size: ${inputSizeMB} MB`);
  console.log(`\n[PROCESSING] Streaming file processing...`);
  
  // Entities to remove for size reduction
  const excludePatterns = [
    'IFCANNOTATION',
    'IFCGRID',
    'IFCGRIDAXIS',        // Millions of these in the file!
    'IFCPROJECTIONELEMENT',
    'IFCSPACE',
    'IFCZONE'
  ];
  
  let processedLines = 0;
  let removedLines = 0;
  let keptLines = 0;
  
  try {
    // Create read and write streams
    const readStream = fs.createReadStream(inputPath, { encoding: 'utf8' });
    const writeStream = fs.createWriteStream(outputPath, { encoding: 'utf8' });
    
    // Create readline interface for line-by-line processing
    const rl = readline.createInterface({
      input: readStream,
      crlfDelay: Infinity // Handle Windows line endings
    });
    
    // Process each line
    for await (const line of rl) {
      processedLines++;
      
      // Always keep header and structure lines
      if (!line.trim() || 
          line.startsWith('/*') || 
          line.startsWith('ISO-') ||
          line.includes('FILE_DESCRIPTION') || 
          line.includes('FILE_NAME') || 
          line.includes('FILE_SCHEMA') ||
          line.includes('ENDSEC') ||
          line.includes('DATA')) {
        writeStream.write(line + '\n');
        keptLines++;
      }
      // Check entity lines for exclusion
      else if (line.includes('=')) {
        let shouldExclude = false;
        
        // Check for excluded patterns
        for (const pattern of excludePatterns) {
          if (line.includes(pattern)) {
            shouldExclude = true;
            removedLines++;
            break;
          }
        }
        
        // Remove extremely long lines (huge meshes)
        if (line.length > 50000) {
          shouldExclude = true;
          removedLines++;
        }
        
        if (!shouldExclude) {
          writeStream.write(line + '\n');
          keptLines++;
        }
      }
      // Keep other lines
      else {
        writeStream.write(line + '\n');
        keptLines++;
      }
      
      // Progress reporting
      if (processedLines % 1000000 === 0) {
        const progressMB = (readStream.bytesRead / (1024 * 1024)).toFixed(1);
        const progressPct = ((readStream.bytesRead / stats.size) * 100).toFixed(1);
        console.log(`   [PROGRESS] ${progressPct}% - ${progressMB}MB - Processed ${processedLines.toLocaleString()}, removed ${removedLines.toLocaleString()}`);
      }
    }
    
    // Close streams
    writeStream.end();
    
    console.log(`\n[COMPLETE] Finishing file write...`);
    
    // Wait for write to complete
    await new Promise((resolve) => {
      writeStream.on('finish', resolve);
    });
    
    const endTime = Date.now();
    const processingTime = ((endTime - startTime) / 1000).toFixed(2);
    
    const outputStats = fs.statSync(outputPath);
    const outputSizeMB = (outputStats.size / (1024 * 1024)).toFixed(2);
    const reductionPct = ((1 - outputStats.size / stats.size) * 100).toFixed(1);
    
    console.log(`\n=== PREPROCESSING COMPLETE ===`);
    console.log(`Original: ${inputSizeMB} MB`);
    console.log(`Preprocessed: ${outputSizeMB} MB`);
    console.log(`Reduction: ${reductionPct}%`);
    console.log(`Lines processed: ${processedLines.toLocaleString()}`);
    console.log(`Lines removed: ${removedLines.toLocaleString()}`);
    console.log(`Lines kept: ${keptLines.toLocaleString()}`);
    console.log(`Time: ${processingTime}s`);
    
    if (parseFloat(reductionPct) > 20) {
      console.log(`✅ Significant size reduction achieved!`);
      console.log(`📁 Ready for conversion: ${outputPath}`);
    } else {
      console.log(`⚠️  Limited size reduction - file may still be challenging`);
    }
    
    return true;
    
  } catch (error) {
    console.error(`❌ Streaming preprocessing failed:`, error.message);
    return false;
  }
}

// Command line usage
const args = process.argv.slice(2);
if (args.length < 1) {
  console.log('Streaming IFC Preprocessor');
  console.log('Usage: node stream_preprocess.cjs <input.ifc> [output.ifc]');
  console.log('');
  console.log('Streams large IFC files to remove non-essential entities:');
  console.log('- Annotations, grids, grid axes, projections, spaces, zones');
  console.log('- Oversized mesh data lines');
  console.log('- Uses streaming to handle files larger than available memory');
  process.exit(1);
}

const inputPath = path.resolve(args[0]);
const outputPath = args[1] 
  ? path.resolve(args[1])
  : inputPath.replace('.ifc', '_preprocessed.ifc');

streamPreprocessIfc(inputPath, outputPath);

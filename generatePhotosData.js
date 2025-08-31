const fs = require("fs");
const path = require("path");

const baseDir = path.join(__dirname, "photos");
const output = [];

// Helper: parse date and name from event folder name (third level)
function parseDateAndName(folderName) {
  // Example folderName:
  // "06-01-2025  - Professional Development to Secretaries - 100 Seater"
  // Extract the date at the start (dd-mm-yyyy), then the rest is event name

  const parts = folderName.split(" - ");
  const datePart = parts[0].trim();  // e.g. "06-01-2025"
  const namePart = parts.slice(1).join(" - ").trim(); // rest

  // Validate date format dd-mm-yyyy
  const dateRegex = /^(\d{2})-(\d{2})-(\d{4})$/;
  const match = datePart.match(dateRegex);

  if (!match) {
    // Invalid date format → treat as malformed folder
    return null;
  }

  const [_, dd, mm, yyyy] = match;
  const dateISO = `${yyyy}-${mm}-${dd}`; // ISO format yyyy-mm-dd

  return { dateISO, namePart };
}

// Recursive scan function
function scanDir(dir, year = "", month = "", eventFolder = "", eventFolderValid = true) {
  const items = fs.readdirSync(dir, { withFileTypes: true });

  // Validate event folder once we reach that level
  if (eventFolder && eventFolderValid) {
    const parsed = parseDateAndName(eventFolder);
    if (!parsed) {
      // Invalid event folder, skip entire folder
      return;
    }
  }

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory()) {
      if (!year) {
        // At year folder level
        scanDir(fullPath, item.name, "", "");
      } else if (!month) {
        // At month folder level
        scanDir(fullPath, year, item.name, "");
      } else if (!eventFolder) {
        // At event folder level
        const isValidEvent = parseDateAndName(item.name) !== null;
        scanDir(fullPath, year, month, item.name, isValidEvent);
      } else {
        // deeper nested, keep same eventFolderValid
        scanDir(fullPath, year, month, eventFolder, eventFolderValid);
      }
    } else if (/\.(jpe?g|png|webp|gif)$/i.test(item.name)) {
      // ONLY add photo if inside a valid event folder (eventFolder must exist and be valid)
      if (!eventFolder || !eventFolderValid) {
        continue; // skip photos outside proper event folders
      }

      // parse event folder name
      const parsed = parseDateAndName(eventFolder);
      if (!parsed) {
        continue; // should not happen due to earlier check, but just in case
      }

      const { dateISO, namePart } = parsed;

      output.push({
        path: path.relative(__dirname, fullPath).replace(/\\/g, "/"),
        year,
        month,
        date: dateISO,
        name: namePart
      });
    }
  }
}

scanDir(baseDir);

// Write JSON & JS files
fs.writeFileSync("photos.json", JSON.stringify(output, null, 2));
console.log(`✅ photos.json generated with ${output.length} photos.`);

const jsContent = `const photos = ${JSON.stringify(output, null, 2)};`;
fs.writeFileSync("photosData.js", jsContent);
console.log("✅ photosData.js created.");

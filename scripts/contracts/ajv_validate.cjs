#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { createRequire } = require("node:module");
const { pathToFileURL } = require("node:url");

function usage(message) {
  if (message) {
    console.error(`error: ${message}`);
  }
  console.error(
    "usage: ajv_validate.cjs <compile|validate> --modules DIR --schema FILE " +
      "[--ref FILE ...] [--data FILE] [--strict log|true|false] [--all-errors]",
  );
  process.exit(2);
}

function parseArguments(argv) {
  if (argv.length === 0) {
    usage("mode is required");
  }

  const mode = argv[0];
  if (mode !== "compile" && mode !== "validate") {
    usage(`unsupported mode: ${mode}`);
  }

  const options = {
    mode,
    modules: "",
    schema: "",
    data: "",
    refs: [],
    strict: mode === "compile" ? "log" : "false",
    allErrors: false,
  };

  for (let index = 1; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--all-errors") {
      options.allErrors = true;
      continue;
    }

    if (!["--modules", "--schema", "--data", "--ref", "--strict"].includes(argument)) {
      usage(`unsupported argument: ${argument}`);
    }
    if (index + 1 >= argv.length) {
      usage(`${argument} requires a value`);
    }
    const value = argv[index + 1];
    index += 1;

    switch (argument) {
      case "--modules":
        options.modules = value;
        break;
      case "--schema":
        options.schema = value;
        break;
      case "--data":
        options.data = value;
        break;
      case "--ref":
        options.refs.push(value);
        break;
      case "--strict":
        if (!["log", "true", "false"].includes(value)) {
          usage("--strict must be log, true or false");
        }
        options.strict = value;
        break;
      default:
        usage(`unsupported argument: ${argument}`);
    }
  }

  if (!options.modules) {
    usage("--modules is required");
  }
  if (!options.schema) {
    usage("--schema is required");
  }
  if (mode === "validate" && !options.data) {
    usage("--data is required for validate mode");
  }
  if (mode === "compile" && options.data) {
    usage("--data is only valid in validate mode");
  }

  return options;
}

function defaultExport(value) {
  return value && value.default ? value.default : value;
}

function loadValidator(modulesDirectory) {
  const absoluteModules = path.resolve(modulesDirectory);
  const resolver = createRequire(path.join(absoluteModules, ".ajv-validator-resolver.cjs"));

  let Ajv2020;
  let addFormats;
  try {
    Ajv2020 = defaultExport(resolver("ajv/dist/2020"));
    addFormats = defaultExport(resolver("ajv-formats"));
  } catch (error) {
    console.error(`error: unable to load pinned AJV modules from ${absoluteModules}`);
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(2);
  }

  return { Ajv2020, addFormats };
}

function readJson(filePath, label) {
  const absolutePath = path.resolve(filePath);
  let text;
  try {
    text = fs.readFileSync(absolutePath, "utf8");
  } catch (error) {
    console.error(`error: unable to read ${label}: ${filePath}`);
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(2);
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    console.error(`error: invalid JSON in ${label}: ${filePath}`);
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

function schemaKey(filePath) {
  return pathToFileURL(path.resolve(filePath)).href;
}

function strictValue(value) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return "log";
}

function createValidator(options) {
  const { Ajv2020, addFormats } = loadValidator(options.modules);
  const ajv = new Ajv2020({
    strict: strictValue(options.strict),
    allErrors: options.allErrors,
    validateFormats: true,
  });
  addFormats(ajv);

  const currentSchema = path.resolve(options.schema);
  const uniqueReferences = [...new Set(options.refs.map((reference) => path.resolve(reference)))].sort();
  for (const reference of uniqueReferences) {
    if (reference === currentSchema) {
      continue;
    }
    const schema = readJson(reference, "reference schema");
    try {
      ajv.addSchema(schema, schemaKey(reference));
    } catch (error) {
      console.error(`error: unable to register reference schema: ${reference}`);
      console.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    }
  }

  const schema = readJson(currentSchema, "schema");
  const key = schemaKey(currentSchema);
  try {
    ajv.addSchema(schema, key);
  } catch (error) {
    console.error(`error: unable to compile schema: ${options.schema}`);
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  }

  const validate = ajv.getSchema(key) || (schema.$id ? ajv.getSchema(schema.$id) : undefined);
  if (typeof validate !== "function") {
    console.error(`error: AJV did not expose a validator for schema: ${options.schema}`);
    process.exit(1);
  }
  return { ajv, validate };
}

function printValidationErrors(ajv, validate, dataPath, lineNumber = 0) {
  const location = lineNumber > 0 ? `${dataPath}:${lineNumber}` : dataPath;
  console.error(`${location} invalid`);
  if (validate.errors && validate.errors.length > 0) {
    console.error(ajv.errorsText(validate.errors, { separator: "\n", dataVar: location }));
  }
}

function validateJsonFile(ajv, validate, dataPath) {
  const data = readJson(dataPath, "data");
  if (!validate(data)) {
    printValidationErrors(ajv, validate, dataPath);
    return false;
  }
  console.log(`${dataPath} valid`);
  return true;
}

function validateJsonLines(ajv, validate, dataPath) {
  let text;
  try {
    text = fs.readFileSync(path.resolve(dataPath), "utf8");
  } catch (error) {
    console.error(`error: unable to read data: ${dataPath}`);
    console.error(error instanceof Error ? error.message : String(error));
    return false;
  }

  let records = 0;
  const lines = text.split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const raw = lines[index].trim();
    if (!raw) {
      continue;
    }
    records += 1;

    let data;
    try {
      data = JSON.parse(raw);
    } catch (error) {
      console.error(`error: invalid JSON in data: ${dataPath}:${index + 1}`);
      console.error(error instanceof Error ? error.message : String(error));
      return false;
    }

    if (!validate(data)) {
      printValidationErrors(ajv, validate, dataPath, index + 1);
      return false;
    }
  }

  if (records === 0) {
    console.error(`error: no JSON records found in data: ${dataPath}`);
    return false;
  }
  console.log(`${dataPath} valid (${records} JSONL records)`);
  return true;
}

const options = parseArguments(process.argv.slice(2));
const { ajv, validate } = createValidator(options);

if (options.mode === "compile") {
  console.log(`schema ${options.schema} is valid`);
  process.exit(0);
}

const valid = options.data.endsWith(".jsonl")
  ? validateJsonLines(ajv, validate, options.data)
  : validateJsonFile(ajv, validate, options.data);
process.exit(valid ? 0 : 1);

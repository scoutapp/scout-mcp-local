#!/usr/bin/env node

import { setup } from './src/lib/setup';

async function main() {
  await setup();
}

main().catch(console.error);
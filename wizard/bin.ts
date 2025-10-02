#!/usr/bin/env node

import { setup } from '@/lib/setup';

async function main() {
  await setup();
}

main().catch(console.error);

#!/usr/bin/env python3

import argparse
import random
import json
import re
import importlib.util
import os.path
import sys
import types
import inspect
import pandas as pd
import numpy as np

MAX_SLOT=8

SMART_COMMENT="\\s*#+\\s*(fastscore|odg)\\.(\\S*)\\s*:\\s*(\\S*)\\s*$"

def is_input_slot(s):
	return s % 2 == 0

## Parse command line
parser = argparse.ArgumentParser()
parser.add_argument("source_file", metavar="MODEL")
parser.add_argument("-i", "--input:0", action="store", help="Name of the input file (slot 0)", metavar="FILE")
parser.add_argument("-o", "--output:1", action="store", help="Name of the output file (slot 1)", metavar="FILE")
parser.add_argument("-b", "--batch-size", action="store", type=int, default=10, help="Name of the output file (slot 1)", metavar="NUM")
#parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
# Add more --input/--output options
for s in range(2,MAX_SLOT):
	tag = "input" if is_input_slot(s) else "output"
	parser.add_argument("--{}:{}".format(tag,s), action="store", help="Name of the {} file (slot {})".format(tag,s), metavar="FILE")

args = parser.parse_args()

def check_scope(scope):
	if scope in ["$all", "$in", "$out"]:
		return scope
	else:
		try:
			return int(scope)
		except ValueError:
			print("Smart comment not recognized")

def default_scope(item):
	if item == "recordsets":
		return "$all"
	elif item == "action":
		return "$in"
	elif item == "slot":
		return "$all"
	elif item == "schema":
		return "$all"
	else:
		return None

def parse_comments1(line, slots):
	if re.match(SMART_COMMENT, line):
		tokens = re.split(SMART_COMMENT,line)
		item0=tokens[2]
		value=tokens[3]
		x=item0.split(".")
		item=x[0]
		scope = check_scope(x[1]) if len(x) > 1 else default_scope(item)
		for s in range(0,MAX_SLOT):
			if scope is None:
				continue
			is_deprecated=False
			if (scope == "$all" or
					scope == "$in" and is_input_slot(s) or
					scope == "$out" and not is_input_slot(s) or
					scope == s):
				if (item == "recordsets"):
					if (value in ["both","none","input","output"]):
						# deprecated style
						if scope != "$all":
							sys.exit("Invalid scope")
						is_deprecated=True
						if (s == 0 or s == 1):
							if (value == "both"):
								slots[s]['recordsets'] = True
							elif (value == "none"):
								slots[s]['recordsets'] = False
							elif (value == "input"):
								slots[s]['recordsets'] = (s == 0)
							elif (value == "output"):
								slots[s]['recordsets'] = (s == 1)
					else:
						# new style
						flag = None
						if (value == "true" or value == "yes"):
							flag = True
						elif (value == "false" or value == "no"):
							flag = False
						else:
							sys.exit("Value '{}' not recognized (use 'true', 'false', 'yes', or 'no')".format(value))
						slots[s]['recordsets']=flag
				elif (item == "action"):
					if not is_input_slot(s):
						sys.exit("An action callback being assigned to an output slot {}".format(s))
					slots[s]['action'] = None if (value == "unused") else value

				# Any mention of a slot makes it active
				if (value != "unused"):
					if (not is_deprecated or s == 0 or s == 1):
						slots[s]['active'] = True

				if (item == "slot"):
					if (value != "unused"):
						sys.exit("Value '{}' not supported (set to 'unused' to disable the slot)".format(value))
					slots[s]['active'] = False


def parse_comments():
	slots = []
	for s in range(0,MAX_SLOT):
		slots.append({
			'action': None,
			'recordsets': False,
			'active': False,
			'file': None
		})
		if is_input_slot(s):
			slots[s]['action'] = "action"

	# By default, slots 0 and 1 are active
	slots[0]['active'] = True
	slots[1]['active'] = True

	f = open(args.source_file)
	for l in f:
		parse_comments1(l, slots)
	f.close()

	return slots

model_slots = parse_comments()

# Collect all data-related options
for k in args.__dict__:
	if (k.startswith("input:") or k.startswith("output:")):
		s = int(k.split(":")[1])
		data_file = args.__dict__[k]
		if not data_file is None:
			if (is_input_slot(s) and not os.path.isfile(data_file)):
				sys.exit("{} not found".format(data_file))
			model_slots[s]['file'] = data_file

# Either all or none input slots must have action set
all_actions=True
none_actions=True
for s in range(0,MAX_SLOT):
	if (not is_input_slot(s)):
		continue
	if (model_slots[s]['action'] is None):
		all_actions=False
	else:
		none_actions=False

if (not all_actions and not none_actions):
	sys.exit("Either all input slots must have action callbacks set or none of them should")

# Check for dangling slots/files
for s in range(0,MAX_SLOT):
	active=model_slots[s]['active']
	data_file=model_slots[s]['file']
	if (active and data_file is None and s != 0 and s != 1):
		sys.exit("Model uses slot {} but there is no data file attached to it".format(s))
	if (not active and not data_file is None):
		sys.exit("Model does not use slot {} but the data file {} is attached to it".format(s,data_file))

inputs=[]
outputs=[]
for s in range(0,MAX_SLOT):
	if not model_slots[s]['active']:
		continue
	if is_input_slot(s):
		inputs.append({
			'slot': s,
			'seq_no': 1,
			'conn': None,
			'entry': None
		})
	else:
		outputs.append({
			'slot': s,
			'conn': None
		})


# Open input files
for i in inputs:
	s = i['slot']
	data_file = model_slots[s]['file']
	conn = open(0) if (s == 0 and data_file is None) else open(data_file)
	i['conn'] = conn

# Open output files
for i in outputs:
	s = i['slot']
	data_file = model_slots[s]['file']
	conn = open(1,'w') if (s == 1 and data_file is None) else open(data_file,'w')
	i['conn'] = conn

# Read a batch of records from the slot
def read_records(s):
	ii = None
	for i in range(0,len(inputs)):
		if inputs[i]['slot'] == s:
			ii = i
			break
	if ii is None:
		if model_slots[s]['active']:
			return None
		else:
			sys.exit("Slot {} is not in use".format(s))

	conn = inputs[ii]['conn']
	seq_no = inputs[ii]['seq_no']

	records = []
	at_eof = False
	while len(records) < args.batch_size:
		l = conn.readline()
		if len(l) == 0:
			if conn.name != 0:
				conn.close()
			inputs.pop(ii)
			at_eof = True
			break

		x = json.loads(l)
		#TODO
    #if (is.list(x) && x$`$fastscore` == "set"):
    #	break
		records.append(x)

	if at_eof and len(records) == 0:
		return []

	if not at_eof:
		old_seq_no = seq_no
		seq_no = seq_no + len(records)
		inputs[ii]['seq_no'] = seq_no

	return records

def as_recordset(records):
	if records is None:
		return None

	return records

	#TODO
	#if (len(records) == 0):
	#	pd.DataFrame(records)
	#else:
	#	head = records[0]

class Slot(object):
	def __init__(self, n):
		self.n = n

	def __iter__(self):
		return self

	def __next__(self):
		data = self.read()
		if data is None:
			raise StopIteration
		else:
			return data

	def read(self):
		if (not is_input_slot(self.n)):
			sys.exit("Model attempts to explicitly read from an output slot {}".format(self.n))
		records = read_records(self.n)
		data = as_recordset(records)
		return data

	def write(self, rec):
		if (is_input_slot(self.n)):
			sys.exit("Model emits data to an input slot {}:".format(s))
		conn = None
		for i in outputs:
			if i['slot'] == self.n:
				conn = i['conn']
				break
		if conn is None:
			sys.exit("Model emits data to an unknown slot {}".format(self.n))

		recordsets = model_slots[self.n]['recordsets']

		if not recordsets:
			print(json.dumps(rec), file=conn)
		else:
			sys.exit("TOODOO")


fio = types.ModuleType("fastscore.io")
fio.__dict__['Slot'] = Slot
sys.modules["fastscore.io"] = fio

spec = importlib.util.spec_from_file_location('model', args.source_file)
mod = importlib.util.module_from_spec(spec)
# Callbacks not resolved yet
spec.loader.exec_module(mod)

# TODO Check/wrap action callbacks
for s in range(0,MAX_SLOT):
	slot = model_slots[s]
	if not slot['active']:
		continue
	if not slot['action'] is None:
		entry = getattr(mod,slot['action'])
		if entry is None:
			sys.exit("A slot {} callback function named '{}' not found".format(s,slot['action']))
		if not isinstance(entry, types.FunctionType):
			sys.exit("A slot {} callback named '{}' must be a function".format(s,slot['action']))
		sig = inspect.signature(entry)
		arity = len(sig.parameters)
		if (arity < 1 or arity > 3):
			sys.exit("A slot {} callback function named '{}' must have arity 1, 2, or 3 (not {})".format(s,slot['action'],arity))
		wrapped_entry = entry
		if arity == 1:
			wrapped_entry = lambda data,slot,seqno: entry(data)
		elif arity == 2:
			wrapped_entry = lambda data,slot,seqno: entry(data,seqno)

		for i in inputs:
			if i['slot'] == s:
				i['entry'] = wrapped_entry


model_uses_callbacks = False
if len(inputs) > 0:
	model_uses_callbacks = isinstance(inputs[0]['entry'], types.FunctionType)

if model_uses_callbacks:
	while len(inputs) > 0:
		# Pick a random slot
		select = random.choice(inputs)
		s = select['slot']

		seq_no = select['seq_no']
		records = read_records(s)

		action = model_slots[s]['action']
		recordsets = model_slots[s]['recordsets']

		if recordsets:
			sys.exit("TODO recordests")
		else:
			# Invoke the callback for each record
			for rec in records:
				print(*select['entry'](rec, s, seq_no)) ## calls 'action'
				seq_no = seq_no + 1

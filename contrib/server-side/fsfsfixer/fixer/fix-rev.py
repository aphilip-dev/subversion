#!/usr/bin/env python

usage = """
Fix a bad FSFS revision file.
Usage: $0 REPO-DIR REVISION
"""

import os, sys, re, subprocess
from subprocess import Popen, PIPE

from find_good_id import FixError, rev_file_path, find_good_id, find_good_rep_header


# ----------------------------------------------------------------------
# Configuration

# Path and file name of the 'svnadmin' and 'svnlook' programs
SVNADMIN = 'svnadmin'
SVNLOOK = 'svnlook'

# Verbosity: True for verbose, or False for quiet
VERBOSE = True

# Global dictionaries recording the fixes made
fixed_ids = {}
fixed_checksums = {}


# ----------------------------------------------------------------------
# Functions

# Print a message, only if 'verbose' mode is enabled.
def verbose_print(str):
  if VERBOSE:
    print str

# Echo the arguments to a log file, and also (if verbose) to standard output.
def log(str):
  #print >>$REPO/fix-ids.log, str
  verbose_print(str)

def run_cmd_quiet(cmd, *args):
  retcode = subprocess.call([cmd] + list(args))
  return retcode

# Execute the command given by CMD and ARGS, and also log it.
def run_cmd(cmd, *args):
  log("CMD: " + cmd + ' ' + ' '.join(list(args)))
  return run_cmd_quiet(cmd, *args)

def replace_in_file(filename, old, new):
  """Replace the string OLD with the string NEW in file FILE.
     Replace all occurrences.  Raise an error if nothing changes."""

  verbose_print("Replacing '" + old + "' in file '" + filename + "'\n" +
                "    with  '" + new + "'")
  # Note: we can't use '/' as a delimiter in the substitution command.
  run_cmd('perl', '-pi.bak', '-e', "s," + old + "," + new + ",", filename)
  if run_cmd_quiet('cmp', '--quiet', filename, filename + '.bak') == 0:
    raise FixError("'" + filename + "' is unchanged after sed substitution.")
  os.remove(filename + '.bak')

def replace_in_rev_file(repo_dir, rev, old, new):
  rev_file = rev_file_path(repo_dir, rev)
  replace_in_file(rev_file, old, new)

# Fix a node-rev ID that has a bad byte-offset part.  Look up the correct
# byte-offset by using the rest of the ID, which necessarily points into an
# older revision or the same revision.  Fix all occurrences within REV_FILE.
#
# ### TODO: Fix occurrences in revisions between <ID revision> and <REV>,
#   since the error reported for <REV> might actually exist in an older
#   revision that is referenced by <REV>.
#
def fix_id(repo_dir, rev, bad_id):

  # Find the GOOD_ID to replace BAD_ID.
  if bad_id == "6-12953.0.r12953/30623":
    good_id = "0-12953.0.r12953/30403"
  else:
    good_id = find_good_id(repo_dir, bad_id)

  # Replacement ID must be the same length, otherwise I don't know how to
  # reconstruct the file so as to preserve all offsets.
  if len(good_id) != len(bad_id):
    raise FixError("Can't handle a replacement ID with a different length: " +
                   "bad id '" + bad_id + "', good id '" + good_id + "'")

  if good_id == bad_id:
    raise FixError("The ID supplied is already correct: " +
                   "good id '" + good_id + "'")

  print "Fixing id: " + bad_id + " -> " + good_id
  replace_in_rev_file(repo_dir, rev, bad_id, good_id)
  fixed_ids[bad_id] = good_id

def fix_checksum(repo_dir, rev, old_checksum, new_checksum):
  """Change all occurrences of OLD_CHECKSUM to NEW_CHECKSUM in the revision
     file for REV in REPO_DIR."""

  assert len(old_checksum) and len(new_checksum)
  assert old_checksum != new_checksum

  print "Fixing checksum: " + old_checksum + " -> " + new_checksum
  replace_in_rev_file(repo_dir, rev, old_checksum, new_checksum)
  fixed_checksums[old_checksum] = new_checksum

def fix_delta_ref(repo_dir, rev, bad_rev, bad_offset, bad_size):
  """Fix a "DELTA <REV> <OFFSET> <SIZE>" line in the revision file for REV
     in REPO_DIR, where <OFFSET> is wrong."""
  good_offset = find_good_rep_header(repo_dir, bad_rev, bad_size)
  old_line = ' '.join(['DELTA', bad_rev, bad_offset, bad_size])
  new_line = ' '.join(['DELTA', bad_rev, good_offset, bad_size])
  print "Fixing delta ref:", old_line, "->", new_line
  replace_in_rev_file(repo_dir, rev, old_line, new_line)


def handle_one_error(repo_dir, rev, error_lines):
  """If ERROR_LINES describes an error we know how to fix, then fix it.
     Return True if fixed, False if not fixed."""

  line1 = error_lines[0]
  match = re.match(r"svn.*: Corrupt node-revision '(.*)'", line1)
  if match:
    # Fix it.
    bad_id = match.group(1)
    verbose_print(error_lines[0])
    fix_id(repo_dir, rev, bad_id)

    # Verify again, and expect to discover a checksum mismatch.
    # verbose_print("Fixed an ID; now verifying to discover the checksum we need to update")
    # error_lines = ...
    # if error_lines[0] != "svn.*: Checksum mismatch while reading representation:":
    #   raise FixError("expected a checksum mismatch after replacing the Id;" +
    #                  "  instead, got this output from 'svnadmin verify -q':" +
    #                  "//".join(error_lines))
    #
    # expected = ...
    # actual   = ...
    # fix_checksum(repo_dir, rev, expected, actual)

    return True

  match = re.match(r"svn.*: Checksum mismatch while reading representation:", line1)
  if match:
    verbose_print(error_lines[0])
    verbose_print(error_lines[1])
    verbose_print(error_lines[2])
    expected = re.match(r' *expected: *([^ ]*)', error_lines[1]).group(1)
    actual   = re.match(r' *actual: *([^ ]*)',   error_lines[2]).group(1)
    fix_checksum(repo_dir, rev, expected, actual)
    return True

  match = re.match(r"svn.*: Corrupt representation '([0-9]*) ([0-9]*) ([0-9]*) .*'", line1)
  if match:
    # Extract the bad reference. We expect only 'offset' is actually bad, in
    # the known kind of corruption that we're targetting.
    bad_rev = match.group(1)
    bad_offset = match.group(2)
    bad_size = match.group(3)
    fix_delta_ref(repo_dir, rev, bad_rev, bad_offset, bad_size)
    return True

  return False

def fix_one_error(repo_dir, rev):
  """Verify, and if there is an error we know how to fix, then fix it.
     Return False if no error, True if fixed, exception if can't fix."""

  # Capture the output of 'svnadmin verify' (ignoring any debug-build output)
  p = Popen([SVNADMIN, 'verify', '-q', '-r'+rev, repo_dir], stdout=PIPE, stderr=PIPE)
  _, stderr = p.communicate()
  svnadmin_err = []
  for line in stderr.splitlines():
    if line.find('(apr_err=') == -1:
      svnadmin_err.append(line)

  if svnadmin_err == []:
    return False

  try:
    if handle_one_error(repo_dir, rev, svnadmin_err):
      return True
  except FixError, e:
    print 'warning:', e
    print "Trying 'svnlook' instead."
    pass

  # At this point, we've got an 'svnadmin' error that we don't know how to
  # handle.  Before giving up, see if 'svnlook' gives a different error,
  # one that we *can* handle.

  # Capture the output of 'svnlook tree' (ignoring any debug-build output)
  p = Popen([SVNLOOK, 'tree', '-r'+rev, repo_dir], stdout=PIPE, stderr=PIPE)
  _, stderr = p.communicate()
  svnlook_err = []
  for line in stderr.splitlines():
    if line.find('(apr_err=') == -1:
      svnlook_err.append(line)

  if svnlook_err == []:
    print 'warning: svnlook did not find an error'
  else:
    if handle_one_error(repo_dir, rev, svnlook_err):
      return True

  raise FixError("unfixable error:\n  " + "\n  ".join(svnadmin_err))


# ----------------------------------------------------------------------
# Main program

def fix_rev(repo_dir, rev):
  """"""

  # Back up the file
  if not os.path.exists(rev_file_path(repo_dir, rev) + '.orig'):
    pass
    # cp -a "$FILE" "$FILE.orig"

  # Keep looking for verification errors in r$REV and fixing them while we can.
  while fix_one_error(repo_dir, rev):
    pass
  print "Revision " + rev + " verifies OK."


if __name__ == '__main__':

  if len(sys.argv) != 3:
    print >>sys.stderr, usage
    exit(1)

  repo_dir = sys.argv[1]
  rev = sys.argv[2]

  try:
    fix_rev(repo_dir, rev)
  except FixError, e:
    print 'error:', e
    exit(1)

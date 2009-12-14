/* fs_skels.h : headers for conversion between fs native types and
 *              skeletons
 *
 * ====================================================================
 *    Licensed to the Apache Software Foundation (ASF) under one
 *    or more contributor license agreements.  See the NOTICE file
 *    distributed with this work for additional information
 *    regarding copyright ownership.  The ASF licenses this file
 *    to you under the Apache License, Version 2.0 (the
 *    "License"); you may not use this file except in compliance
 *    with the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing,
 *    software distributed under the License is distributed on an
 *    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 *    KIND, either express or implied.  See the License for the
 *    specific language governing permissions and limitations
 *    under the License.
 * ====================================================================
 */

#ifndef SVN_LIBSVN_FS_FS_SKELS_H
#define SVN_LIBSVN_FS_FS_SKELS_H

#define SVN_WANT_BDB
#include "svn_private_config.h"

#include <apr_pools.h>
#include <apr_hash.h>

#include "svn_fs.h"
#include "../fs.h"
#include "private/svn_skel.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/*** Parsing (conversion from skeleton to native FS type) ***/


/* Parse a `REVISION' SKEL into *REVISION_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__parse_revision_skel(revision_t **revision_p,
                                 svn_skel_t *skel,
                                 apr_pool_t *pool);

/* Parse a `TRANSACTION' SKEL into *TRANSACTION_P.  Use POOL for all
   allocations.  FORMAT is the format version of the filesystem. */
svn_error_t *
svn_fs_base__parse_transaction_skel(transaction_t **transaction_p,
                                    svn_skel_t *skel,
                                    int format,
                                    apr_pool_t *pool);

/* Parse a `REPRESENTATION' SKEL into *REP_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__parse_representation_skel(representation_t **rep_p,
                                       svn_skel_t *skel,
                                       apr_pool_t *pool);

/* Parse a `NODE-REVISION' SKEL into *NODEREV_P.  Use POOL for all
   allocations. */
svn_error_t *
svn_fs_base__parse_node_revision_skel(node_revision_t **noderev_p,
                                      svn_skel_t *skel,
                                      apr_pool_t *pool);

/* Parse a `COPY' SKEL into *COPY_P.  Use POOL for all allocations. */
svn_error_t *
svn_fs_base__parse_copy_skel(copy_t **copy_p,
                             svn_skel_t *skel,
                             apr_pool_t *pool);

/* Parse an `ENTRIES' SKEL into *ENTRIES_P, which is a hash with const
   char * names (the directory entry name) and svn_fs_id_t * values
   (the node-id of the entry), or NULL if SKEL contains no entries.
   Use POOL for all allocations. */
svn_error_t *
svn_fs_base__parse_entries_skel(apr_hash_t **entries_p,
                                svn_skel_t *skel,
                                apr_pool_t *pool);

/* Parse a `CHANGE' SKEL into *CHANGE_P.  Use POOL for all allocations. */
svn_error_t *
svn_fs_base__parse_change_skel(change_t **change_p,
                               svn_skel_t *skel,
                               apr_pool_t *pool);

/* Parse a `LOCK' SKEL into *LOCK_P.  Use POOL for all allocations. */
svn_error_t *
svn_fs_base__parse_lock_skel(svn_lock_t **lock_p,
                             svn_skel_t *skel,
                             apr_pool_t *pool);



/*** Unparsing (conversion from native FS type to skeleton) ***/


/* Unparse REVISION into a `REVISION' skel *SKEL_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__unparse_revision_skel(svn_skel_t **skel_p,
                                   const revision_t *revision,
                                   apr_pool_t *pool);

/* Unparse TRANSACTION into a `TRANSACTION' skel *SKEL_P.  Use POOL
   for all allocations.  FORMAT is the format version of the filesystem. */
svn_error_t *
svn_fs_base__unparse_transaction_skel(svn_skel_t **skel_p,
                                      const transaction_t *transaction,
                                      int format,
                                      apr_pool_t *pool);

/* Unparse REP into a `REPRESENTATION' skel *SKEL_P.  Use POOL for all
   allocations.  FORMAT is the format version of the filesystem. */
svn_error_t *
svn_fs_base__unparse_representation_skel(svn_skel_t **skel_p,
                                         const representation_t *rep,
                                         int format,
                                         apr_pool_t *pool);

/* Unparse NODEREV into a `NODE-REVISION' skel *SKEL_P.  Use POOL for
   all allocations.  FORMAT is the format version of the filesystem. */
svn_error_t *
svn_fs_base__unparse_node_revision_skel(svn_skel_t **skel_p,
                                        const node_revision_t *noderev,
                                        int format,
                                        apr_pool_t *pool);

/* Unparse COPY into a `COPY' skel *SKEL_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__unparse_copy_skel(svn_skel_t **skel_p,
                               const copy_t *copy,
                               apr_pool_t *pool);

/* Unparse an ENTRIES hash, which has const char * names (the entry
   name) and svn_fs_id_t * values (the node-id of the entry) into an
   `ENTRIES' skel *SKEL_P.  Use POOL for all allocations.  */
svn_error_t *
svn_fs_base__unparse_entries_skel(svn_skel_t **skel_p,
                                  apr_hash_t *entries,
                                  apr_pool_t *pool);

/* Unparse CHANGE into a `CHANGE' skel *SKEL_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__unparse_change_skel(svn_skel_t **skel_p,
                                 const change_t *change,
                                 apr_pool_t *pool);

/* Unparse LOCK into a `LOCK' skel *SKEL_P.  Use POOL for all
   allocations.  */
svn_error_t *
svn_fs_base__unparse_lock_skel(svn_skel_t **skel_p,
                               const svn_lock_t *lock,
                               apr_pool_t *pool);



#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* SVN_LIBSVN_FS_FS_SKELS_H */

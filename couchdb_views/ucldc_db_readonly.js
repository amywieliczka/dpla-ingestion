{
   "_id": "_design/readonly",
   "language": "javascript",
   "validate_doc_update": "function(newDoc, oldDoc, userCtx) {
            if (userCtx.roles.indexOf('_admin') !== -1) {
                return;
            } else {
                throw({forbidden: 'Only admins may edit the database'});
            }
        }" 
}

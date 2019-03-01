from bika.health import logger
from bika.lims import api
from bika.lims.catalog.catalog_utilities import addZCTextIndex


def setup_catalogs(catalogs_by_type, indexes_by_catalog,
                   columns_by_catalog):
    """Setup Plone catalogs
    """
    logger.info("Setup Catalogs ...")

    # Setup catalogs by type
    for type_name, catalogs in catalogs_by_type:
        at = api.get_tool("archetype_tool")
        # get the current registered catalogs
        current_catalogs = at.getCatalogsByType(type_name)
        # get the desired catalogs this type should be in
        desired_catalogs = map(api.get_tool, catalogs)
        # check if the catalogs changed for this portal_type
        if set(desired_catalogs).difference(current_catalogs):
            # fetch the brains to reindex
            brains = api.search({"portal_type": type_name})
            # updated the catalogs
            at.setCatalogsByType(type_name, catalogs)
            logger.info("Assign '%s' type to Catalogs %s" %
                        (type_name, catalogs))
            for brain in brains:
                obj = api.get_object(brain)
                logger.info("Reindexing '%s'" % repr(obj))
                obj.reindexObject()

    # Setup catalog indexes
    to_index = []
    for catalog, name, meta_type in indexes_by_catalog:
        c = api.get_tool(catalog)
        indexes = c.indexes()
        if name in indexes:
            logger.info("Index '%s' already in Catalog [SKIP]" % name)
            continue

        logger.info("Adding Index '%s' for field '%s' to catalog '%s"
                    % (meta_type, name, catalog))
        if meta_type == "ZCTextIndex":
            addZCTextIndex(c, name)
        else:
            c.addIndex(name, meta_type)
        to_index.append((c, name))
        logger.info("Added Index '%s' for field '%s' to catalog [DONE]"
                    % (meta_type, name))

    for catalog, name in to_index:
        logger.info("Indexing new index '%s' ..." % name)
        catalog.manage_reindexIndex(name)
        logger.info("Indexing new index '%s' [DONE]" % name)

    # Setup catalog metadata columns
    for catalog, name in columns_by_catalog:
        c = api.get_tool(catalog)
        if name not in c.schema():
            logger.info("Adding Column '%s' to catalog '%s' ..."
                        % (name, catalog))
            c.addColumn(name)
            logger.info("Added Column '%s' to catalog '%s' [DONE]"
                        % (name, catalog))
        else:
            logger.info("Column '%s' already in catalog '%s'  [SKIP]"
                        % (name, catalog))
            continue


def del_index(catalog_id, name):
    """Removes the given index from the catalog
    """
    catalog = api.get_tool(catalog_id)
    if name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}'".format(name, catalog_id))
        return False
    catalog.delIndex(name)
    logger.info("Index '{}' removed from '{}'".format(name, catalog_id))
    return True


def del_column(catalog_id, name):
    """Removes the given metadata column from the catalog
    """
    catalog = api.get_tool(catalog_id)
    if name not in catalog.schema():
        logger.info("Column '{}' not in catalog '{}'".format(name, catalog_id))
        return False
    catalog.delColumn(name)
    logger.info("Column '{}' removed from '{}'".format(name, catalog_id))
    return True

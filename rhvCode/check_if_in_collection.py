def checkIfProdInCollection(storeUrl, excludedCollectionIds ):
	# passed: list of generic collections to avoid

	# delete all table rows for that storeUrl:
	ProdUrls = prodColItem.objects.filter(pc_i_store_url__iexact=store_url)
		for row in ProdUrls:
			ProdUrls.delete()

	# get all products
	for product 				in 	products create an array
		prodCollectionIdList 	= 	"empty"
		prodDict[prodId] 		= 	(product.title, product.handle, prodCollectionIdList)

# get all collections
	for collection in AllCollections:
		if collect.id not in excludedCollectionIds:
			for product in collection.products:
				prodCollectionIdList = prodDict[prodId][2]+","+str(collection.id)
				prodDict[prodId]	=(product.title, product.handle, prodCollectionIdList)


	for prodId in ProdDict
		prodTitle					=	ProdDict[prodId][0]
		prodHandle					=	ProdDict[prodId][2]
		prodCollectionIdList		=	ProdDict[prodId][3]

		pc_i_store_url_ch 			=	store_url
		if prodCollectionIdList 	== "empty": 
			pc_i_found_bool 		= False
			pc_i_info = (	<td>'<a href="'+str(storeUrl)+'/admin/products/'+str(prodId)+'">Edit</a><td>'+
							<td>'<a href="'+str(storeUrl)+'/products/'+str(prodHandle)+'>'+str(prodTitle)+'</a><td>'
							)

		else:	
			pc_i_found_bool 		= True

		# pc_i_fixed_bool  defaults to false	

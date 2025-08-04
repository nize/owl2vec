```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?property (COUNT(?property) AS ?count)
WHERE {
  # Find any triple using a property
  ?s ?property ?o .
  # Filter to ensure the property is an AnnotationProperty
  ?property a owl:AnnotationProperty .
}
GROUP BY ?property
ORDER BY DESC(?count)
```

property,count
http://www.w3.org/2004/02/skos/core#note,"12,258"
http://www.w3.org/2004/02/skos/core#definition,"7,756"
http://www.w3.org/2004/02/skos/core#altLabel,"1,991"
https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym,"1,988"
https://www.omg.org/spec/Commons/AnnotationVocabulary/explanatoryNote,"1,915"
http://purl.org/dc/terms/source,"1,156"
https://www.omg.org/spec/Commons/AnnotationVocabulary/adaptedFrom,957
https://www.omg.org/spec/Commons/AnnotationVocabulary/abbreviation,809
http://www.w3.org/2002/07/owl#minQualifiedCardinality,530
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/commonDesignation,502
http://purl.org/dc/terms/description,408
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/preferredDesignation,384
http://www.w3.org/2004/02/skos/core#example,237
http://www.w3.org/2004/02/skos/core#editorialNote,96
https://www.omg.org/spec/Commons/AnnotationVocabulary/usageNote,66
http://www.w3.org/2004/02/skos/core#isNarrowerThan,64
http://www.w3.org/2004/02/skos/core#scopeNote,38
https://www.omg.org/spec/Commons/AnnotationVocabulary/directSource,18
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/definitionOrigin,17
http://www.w3.org/2004/02/skos/core#prefLabel,9
https://www.omg.org/spec/Commons/AnnotationVocabulary/symbol,4
https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym,3
https://www.omg.org/spec/Commons/AnnotationVocabulary/copyright,2
http://purl.org/dc/terms/rights,2
http://www.omg.org/techprocess/ab/SpecificationMetadata/directSource,2
http://purl.org/dc/terms/abstract,1
http://purl.org/dc/terms/issued,1
http://purl.org/dc/terms/license,1
http://purl.org/dc/terms/modified,1
http://www.w3.org/2004/02/skos/core#historyNote,1

Of these I select the following to start with:
http://www.w3.org/2004/02/skos/core#note,"12,258"
http://www.w3.org/2004/02/skos/core#definition,"7,756"
http://www.w3.org/2004/02/skos/core#altLabel,"1,991"
https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym,"1,988"
https://www.omg.org/spec/Commons/AnnotationVocabulary/explanatoryNote,"1,915"
https://www.omg.org/spec/Commons/AnnotationVocabulary/abbreviation,809
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/commonDesignation,502
http://purl.org/dc/terms/description,408
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/preferredDesignation,384
http://www.w3.org/2004/02/skos/core#example,237
http://www.w3.org/2004/02/skos/core#editorialNote,96
https://www.omg.org/spec/Commons/AnnotationVocabulary/usageNote,66
http://www.w3.org/2004/02/skos/core#scopeNote,38
http://www.w3.org/2004/02/skos/core#prefLabel,9
https://www.omg.org/spec/Commons/AnnotationVocabulary/symbol,4
https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym,3
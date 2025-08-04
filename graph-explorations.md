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
```

### Of these I select the following to start with
```
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
```


### Checking which are single/multiple

```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?property (IF(MAX(?perSubjectCount) > 1, "multiple"^^xsd:string, "single"^^xsd:string) AS ?occurrenceType)
WHERE {
  # This inner query remains the same.
  # It calculates the count for each specific subject-property pair.
  {
    SELECT ?s ?property (COUNT(?o) AS ?perSubjectCount)
    WHERE {
      ?s ?property ?o .
      ?property a owl:AnnotationProperty .
    }
    GROUP BY ?s ?property
  }
}
GROUP BY ?property
# The change is here: We sum the per-subject counts to get a total for ordering.
ORDER BY DESC(SUM(?perSubjectCount))
```

```
property,occurrenceType
http://www.w3.org/2004/02/skos/core#note,multiple
http://www.w3.org/2004/02/skos/core#definition,multiple
http://www.w3.org/2004/02/skos/core#altLabel,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/explanatoryNote,multiple
http://purl.org/dc/terms/source,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/adaptedFrom,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/abbreviation,multiple
http://www.w3.org/2002/07/owl#minQualifiedCardinality,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/commonDesignation,multiple
http://purl.org/dc/terms/description,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/preferredDesignation,single
http://www.w3.org/2004/02/skos/core#example,multiple
http://www.w3.org/2004/02/skos/core#editorialNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/usageNote,multiple
http://www.w3.org/2004/02/skos/core#isNarrowerThan,multiple
http://www.w3.org/2004/02/skos/core#scopeNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/directSource,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/definitionOrigin,single
http://www.w3.org/2004/02/skos/core#prefLabel,single
https://www.omg.org/spec/Commons/AnnotationVocabulary/symbol,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym,single
https://www.omg.org/spec/Commons/AnnotationVocabulary/copyright,multiple
http://purl.org/dc/terms/rights,multiple
http://www.omg.org/techprocess/ab/SpecificationMetadata/directSource,single
http://purl.org/dc/terms/abstract,single
http://purl.org/dc/terms/issued,single
http://purl.org/dc/terms/license,single
http://purl.org/dc/terms/modified,single
http://www.w3.org/2004/02/skos/core#historyNote,single
```

### My selection
```
http://www.w3.org/2004/02/skos/core#note,multiple
http://www.w3.org/2004/02/skos/core#definition,multiple
http://www.w3.org/2004/02/skos/core#altLabel,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/explanatoryNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/abbreviation,multiple
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/commonDesignation,multiple
http://purl.org/dc/terms/description,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/preferredDesignation,single
http://www.w3.org/2004/02/skos/core#example,multiple
http://www.w3.org/2004/02/skos/core#editorialNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/usageNote,multiple
http://www.w3.org/2004/02/skos/core#scopeNote,multiple
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/definitionOrigin,single
http://www.w3.org/2004/02/skos/core#prefLabel,single
https://www.omg.org/spec/Commons/AnnotationVocabulary/symbol,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym,single
http://purl.org/dc/terms/abstract,single
http://www.w3.org/2004/02/skos/core#historyNote,single
```

### Realized I missed built-in annotations
```
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?property (IF(MAX(?perSubjectCount) > 1, "multiple"^^xsd:string, "single"^^xsd:string) AS ?occurrenceType)
WHERE {
  # This subquery now gets counts for ALL properties first
  {
    SELECT ?s ?property (COUNT(?o) AS ?perSubjectCount)
    WHERE {
      ?s ?property ?o .
    }
    GROUP BY ?s ?property
  }

  # This block now filters for the properties we want
  {
    # Option 1: The property is explicitly declared as an AnnotationProperty
    ?property a owl:AnnotationProperty .
  }
  UNION
  {
    # Option 2: The property is one of the built-in annotation properties
    VALUES ?property {
      rdfs:label
      rdfs:comment
      rdfs:seeAlso
      rdfs:isDefinedBy
      owl:versionInfo
    }
  }
}
GROUP BY ?property
ORDER BY DESC(SUM(?perSubjectCount))
```
```
property,occurrenceType
http://www.w3.org/2000/01/rdf-schema#label,multiple
http://www.w3.org/2004/02/skos/core#note,multiple
http://www.w3.org/2004/02/skos/core#definition,multiple
http://www.w3.org/2000/01/rdf-schema#seeAlso,multiple
http://www.w3.org/2000/01/rdf-schema#isDefinedBy,single
http://www.w3.org/2004/02/skos/core#altLabel,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/explanatoryNote,multiple
http://purl.org/dc/terms/source,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/adaptedFrom,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/abbreviation,multiple
http://www.w3.org/2002/07/owl#minQualifiedCardinality,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/commonDesignation,multiple
http://purl.org/dc/terms/description,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/preferredDesignation,single
http://www.w3.org/2004/02/skos/core#example,multiple
http://www.w3.org/2004/02/skos/core#editorialNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/usageNote,multiple
http://www.w3.org/2004/02/skos/core#isNarrowerThan,multiple
http://www.w3.org/2004/02/skos/core#scopeNote,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/directSource,single
https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/definitionOrigin,single
http://www.w3.org/2004/02/skos/core#prefLabel,single
http://www.w3.org/2000/01/rdf-schema#comment,single
https://www.omg.org/spec/Commons/AnnotationVocabulary/symbol,multiple
https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym,single
https://www.omg.org/spec/Commons/AnnotationVocabulary/copyright,multiple
http://purl.org/dc/terms/rights,multiple
http://www.omg.org/techprocess/ab/SpecificationMetadata/directSource,single
http://purl.org/dc/terms/abstract,single
http://purl.org/dc/terms/issued,single
http://purl.org/dc/terms/license,single
http://purl.org/dc/terms/modified,single
http://www.w3.org/2004/02/skos/core#historyNote,single
```

### Instead of listing all explictly I think it makes sense to instead use an exclusion list
http://purl.org/dc/terms/issued
http://purl.org/dc/terms/license
http://purl.org/dc/terms/modified
https://www.omg.org/spec/Commons/AnnotationVocabulary/copyright
http://purl.org/dc/terms/rights
http://www.omg.org/techprocess/ab/SpecificationMetadata/directSource
http://www.w3.org/2002/07/owl#minQualifiedCardinality
http://purl.org/dc/terms/source
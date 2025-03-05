# IRMAI Knowledge Extractor &amp; Context Builder Agent








cd /c/samadhi/personal/side_hustle/IRMAI
rm -rf collection
mkdir collection
find IRMAI-Knowledge-Extractor-Context-Builder-Agent -path "IRMAI-Knowledge-Extractor-Context-Builder-Agent/IRMAI-Knowledge-Extractor-Context-Builder-Agent" -prune -o -type f \( -name "*.py" -o -name "*.txt" -o -name "*.yaml" -o -name "*.json" \) -exec cp {} collection/ \;

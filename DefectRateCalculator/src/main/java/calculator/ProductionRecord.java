package calculator;

public class ProductionRecord {

    private final int defectiveCount;
    private final int totalCount;

    public ProductionRecord(int defectiveCount, int totalCount) {
        this.defectiveCount = defectiveCount;
        this.totalCount = totalCount;
    }

    public int getDefectiveCount() { return defectiveCount; }
    public int getTotalCount()     { return totalCount; }
}

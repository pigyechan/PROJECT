package calculator.claude;

public class ClaudeProductionRecord {

    private final int defectiveCount;
    private final int totalCount;

    public ClaudeProductionRecord(int defectiveCount, int totalCount) {
        this.defectiveCount = defectiveCount;
        this.totalCount = totalCount;
    }

    public int getDefectiveCount() { return defectiveCount; }
    public int getTotalCount()     { return totalCount; }
}

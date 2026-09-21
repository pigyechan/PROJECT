package climbingcrew.record;

import java.util.List;

/**
 * GET /records 의 인라인 응답 스키마(items/page/size/totalCount)에 대응하는 DTO.
 */
public class RecordListResponse {

    private List<RecordResponse> items;
    private int page;
    private int size;
    private long totalCount;

    public List<RecordResponse> getItems() {
        return items;
    }

    public void setItems(List<RecordResponse> items) {
        this.items = items;
    }

    public int getPage() {
        return page;
    }

    public void setPage(int page) {
        this.page = page;
    }

    public int getSize() {
        return size;
    }

    public void setSize(int size) {
        this.size = size;
    }

    public long getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(long totalCount) {
        this.totalCount = totalCount;
    }
}

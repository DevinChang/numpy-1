# pylint: disable-msg=W0611, W0612, W0511
"""Tests suite for MaskedArray.
Adapted from the original test_ma by Pierre Gerard-Marchant

:author: Pierre Gerard-Marchant
:contact: pierregm_at_uga_dot_edu
:version: $Id: test_extras.py 3473 2007-10-29 15:18:13Z jarrod.millman $
"""
__author__ = "Pierre GF Gerard-Marchant ($Author: jarrod.millman $)"
__version__ = '1.0'
__revision__ = "$Revision: 3473 $"
__date__     = '$Date: 2007-10-29 17:18:13 +0200 (Mon, 29 Oct 2007) $'

import numpy as np
from numpy.testing import TestCase, run_module_suite
from numpy.ma.testutils import *
from numpy.ma.core import *
from numpy.ma.extras import *


class TestGeneric(TestCase):
    #
    def test_masked_all(self):
        "Tests masked_all"
        # Standard dtype
        test = masked_all((2,), dtype=float)
        control = array([1, 1], mask=[1, 1], dtype=float)
        assert_equal(test, control)
        # Flexible dtype
        dt = np.dtype({'names': ['a', 'b'], 'formats': ['f', 'f']})
        test = masked_all((2,), dtype=dt)
        control = array([(0, 0), (0, 0)], mask=[(1, 1), (1, 1)], dtype=dt)
        assert_equal(test, control)
        test = masked_all((2,2), dtype=dt)
        control = array([[(0, 0), (0, 0)], [(0, 0), (0, 0)]],
                        mask=[[(1, 1), (1, 1)], [(1, 1), (1, 1)]],
                        dtype=dt)
        assert_equal(test, control)
        # Nested dtype
        dt = np.dtype([('a','f'), ('b', [('ba', 'f'), ('bb', 'f')])])
        test = masked_all((2,), dtype=dt)
        control = array([(1, (1, 1)), (1, (1, 1))],
                         mask=[(1, (1, 1)), (1, (1, 1))], dtype=dt)
        assert_equal(test, control)
        test = masked_all((2,), dtype=dt)
        control = array([(1, (1, 1)), (1, (1, 1))],
                         mask=[(1, (1, 1)), (1, (1, 1))], dtype=dt)
        assert_equal(test, control)
        test = masked_all((1,1), dtype=dt)
        control = array([[(1, (1, 1))]], mask=[[(1, (1, 1))]], dtype=dt)
        assert_equal(test, control)


    def test_masked_all_like(self):
        "Tests masked_all"
        # Standard dtype
        base = array([1, 2], dtype=float)
        test = masked_all_like(base)
        control = array([1, 1], mask=[1, 1], dtype=float)
        assert_equal(test, control)
        # Flexible dtype
        dt = np.dtype({'names': ['a', 'b'], 'formats': ['f', 'f']})
        base = array([(0, 0), (0, 0)], mask=[(1, 1), (1, 1)], dtype=dt)
        test = masked_all_like(base)
        control = array([(10, 10), (10, 10)], mask=[(1, 1), (1, 1)], dtype=dt)
        assert_equal(test, control)
        # Nested dtype
        dt = np.dtype([('a','f'), ('b', [('ba', 'f'), ('bb', 'f')])])
        control = array([(1, (1, 1)), (1, (1, 1))],
                        mask=[(1, (1, 1)), (1, (1, 1))], dtype=dt)
        test = masked_all_like(control)
        assert_equal(test, control)
        #


class TestAverage(TestCase):
    "Several tests of average. Why so many ? Good point..."
    def test_testAverage1(self):
        "Test of average."
        ott = array([0.,1.,2.,3.], mask=[1,0,0,0])
        assert_equal(2.0, average(ott,axis=0))
        assert_equal(2.0, average(ott, weights=[1., 1., 2., 1.]))
        result, wts = average(ott, weights=[1.,1.,2.,1.], returned=1)
        assert_equal(2.0, result)
        self.failUnless(wts == 4.0)
        ott[:] = masked
        assert_equal(average(ott,axis=0).mask, [True])
        ott = array([0.,1.,2.,3.], mask=[1,0,0,0])
        ott = ott.reshape(2,2)
        ott[:,1] = masked
        assert_equal(average(ott,axis=0), [2.0, 0.0])
        assert_equal(average(ott,axis=1).mask[0], [True])
        assert_equal([2.,0.], average(ott, axis=0))
        result, wts = average(ott, axis=0, returned=1)
        assert_equal(wts, [1., 0.])

    def test_testAverage2(self):
        "More tests of average."
        w1 = [0,1,1,1,1,0]
        w2 = [[0,1,1,1,1,0],[1,0,0,0,0,1]]
        x = arange(6, dtype=float_)
        assert_equal(average(x, axis=0), 2.5)
        assert_equal(average(x, axis=0, weights=w1), 2.5)
        y = array([arange(6, dtype=float_), 2.0*arange(6)])
        assert_equal(average(y, None), np.add.reduce(np.arange(6))*3./12.)
        assert_equal(average(y, axis=0), np.arange(6) * 3./2.)
        assert_equal(average(y, axis=1),
                     [average(x,axis=0), average(x,axis=0) * 2.0])
        assert_equal(average(y, None, weights=w2), 20./6.)
        assert_equal(average(y, axis=0, weights=w2),
                     [0.,1.,2.,3.,4.,10.])
        assert_equal(average(y, axis=1),
                     [average(x,axis=0), average(x,axis=0) * 2.0])
        m1 = zeros(6)
        m2 = [0,0,1,1,0,0]
        m3 = [[0,0,1,1,0,0],[0,1,1,1,1,0]]
        m4 = ones(6)
        m5 = [0, 1, 1, 1, 1, 1]
        assert_equal(average(masked_array(x, m1),axis=0), 2.5)
        assert_equal(average(masked_array(x, m2),axis=0), 2.5)
        assert_equal(average(masked_array(x, m4),axis=0).mask, [True])
        assert_equal(average(masked_array(x, m5),axis=0), 0.0)
        assert_equal(count(average(masked_array(x, m4),axis=0)), 0)
        z = masked_array(y, m3)
        assert_equal(average(z, None), 20./6.)
        assert_equal(average(z, axis=0), [0.,1.,99.,99.,4.0, 7.5])
        assert_equal(average(z, axis=1), [2.5, 5.0])
        assert_equal(average(z,axis=0, weights=w2), [0.,1., 99., 99., 4.0, 10.0])

    def test_testAverage3(self):
        "Yet more tests of average!"
        a = arange(6)
        b = arange(6) * 3
        r1, w1 = average([[a,b],[b,a]], axis=1, returned=1)
        assert_equal(shape(r1) , shape(w1))
        assert_equal(r1.shape , w1.shape)
        r2, w2 = average(ones((2,2,3)), axis=0, weights=[3,1], returned=1)
        assert_equal(shape(w2) , shape(r2))
        r2, w2 = average(ones((2,2,3)), returned=1)
        assert_equal(shape(w2) , shape(r2))
        r2, w2 = average(ones((2,2,3)), weights=ones((2,2,3)), returned=1)
        assert_equal(shape(w2), shape(r2))
        a2d = array([[1,2],[0,4]], float)
        a2dm = masked_array(a2d, [[0,0],[1,0]])
        a2da = average(a2d, axis=0)
        assert_equal(a2da, [0.5, 3.0])
        a2dma = average(a2dm, axis=0)
        assert_equal(a2dma, [1.0, 3.0])
        a2dma = average(a2dm, axis=None)
        assert_equal(a2dma, 7./3.)
        a2dma = average(a2dm, axis=1)
        assert_equal(a2dma, [1.5, 4.0])

class TestConcatenator(TestCase):
    "Tests for mr_, the equivalent of r_ for masked arrays."
    def test_1d(self):
        "Tests mr_ on 1D arrays."
        assert_array_equal(mr_[1,2,3,4,5,6],array([1,2,3,4,5,6]))
        b = ones(5)
        m = [1,0,0,0,0]
        d = masked_array(b,mask=m)
        c = mr_[d,0,0,d]
        self.failUnless(isinstance(c,MaskedArray) or isinstance(c,core.MaskedArray))
        assert_array_equal(c,[1,1,1,1,1,0,0,1,1,1,1,1])
        assert_array_equal(c.mask, mr_[m,0,0,m])

    def test_2d(self):
        "Tests mr_ on 2D arrays."
        a_1 = rand(5,5)
        a_2 = rand(5,5)
        m_1 = np.round_(rand(5,5),0)
        m_2 = np.round_(rand(5,5),0)
        b_1 = masked_array(a_1,mask=m_1)
        b_2 = masked_array(a_2,mask=m_2)
        d = mr_['1',b_1,b_2]  # append columns
        self.failUnless(d.shape == (5,10))
        assert_array_equal(d[:,:5],b_1)
        assert_array_equal(d[:,5:],b_2)
        assert_array_equal(d.mask, np.r_['1',m_1,m_2])
        d = mr_[b_1,b_2]
        self.failUnless(d.shape == (10,5))
        assert_array_equal(d[:5,:],b_1)
        assert_array_equal(d[5:,:],b_2)
        assert_array_equal(d.mask, np.r_[m_1,m_2])



class TestNotMasked(TestCase):
    "Tests notmasked_edges and notmasked_contiguous."
    def test_edges(self):
        "Tests unmasked_edges"
        data = masked_array(np.arange(25).reshape(5, 5),
                            mask=[[0, 0, 1, 0, 0],
                                  [0, 0, 0, 1, 1],
                                  [1, 1, 0, 0, 0],
                                  [0, 0, 0, 0, 0],
                                  [1, 1, 1, 0, 0]],)
        test = notmasked_edges(data, None)
        assert_equal(test, [0, 24])
        test = notmasked_edges(data, 0)
        assert_equal(test[0], [(0, 0, 1, 0, 0), (0, 1, 2, 3, 4)])
        assert_equal(test[1], [(3, 3, 3, 4, 4), (0, 1, 2, 3, 4)])
        test = notmasked_edges(data, 1)
        assert_equal(test[0], [(0, 1, 2, 3, 4), (0, 0, 2, 0, 3)])
        assert_equal(test[1], [(0, 1, 2, 3, 4), (4, 2, 4, 4, 4)])
        #
        test = notmasked_edges(data.data, None)
        assert_equal(test, [0, -1])
        test = notmasked_edges(data.data, 0)
        assert_equal(test[0], [(0, 0, 0, 0, 0), (0, 1, 2, 3, 4)])
        assert_equal(test[1], [(4, 4, 4, 4, 4), (0, 1, 2, 3, 4)])
        test = notmasked_edges(data.data, -1)
        assert_equal(test[0], [(0, 1, 2, 3, 4), (0, 0, 0, 0, 0)])
        assert_equal(test[1], [(0, 1, 2, 3, 4), (4, 4, 4, 4, 4)])
        #
        data[-2] = masked
        test = notmasked_edges(data, 0)
        assert_equal(test[0], [(0, 0, 1, 0, 0), (0, 1, 2, 3, 4)])
        assert_equal(test[1], [(1, 1, 2, 4, 4), (0, 1, 2, 3, 4)])
        test = notmasked_edges(data, -1)
        assert_equal(test[0], [(0, 1, 2, 4), (0, 0, 2, 3)])
        assert_equal(test[1], [(0, 1, 2, 4), (4, 2, 4, 4)])



    def test_contiguous(self):
        "Tests notmasked_contiguous"
        a = masked_array(np.arange(24).reshape(3,8),
                         mask=[[0,0,0,0,1,1,1,1],
                               [1,1,1,1,1,1,1,1],
                               [0,0,0,0,0,0,1,0],])
        tmp = notmasked_contiguous(a, None)
        assert_equal(tmp[-1], slice(23,23,None))
        assert_equal(tmp[-2], slice(16,21,None))
        assert_equal(tmp[-3], slice(0,3,None))
        #
        tmp = notmasked_contiguous(a, 0)
        self.failUnless(len(tmp[-1]) == 1)
        self.failUnless(tmp[-2] is None)
        assert_equal(tmp[-3],tmp[-1])
        self.failUnless(len(tmp[0]) == 2)
        #
        tmp = notmasked_contiguous(a, 1)
        assert_equal(tmp[0][-1], slice(0,3,None))
        self.failUnless(tmp[1] is None)
        assert_equal(tmp[2][-1], slice(7,7,None))
        assert_equal(tmp[2][-2], slice(0,5,None))




class Test2DFunctions(TestCase):
    "Tests 2D functions"
    def test_compress2d(self):
        "Tests compress2d"
        x = array(np.arange(9).reshape(3,3), mask=[[1,0,0],[0,0,0],[0,0,0]])
        assert_equal(compress_rowcols(x), [[4,5],[7,8]] )
        assert_equal(compress_rowcols(x,0), [[3,4,5],[6,7,8]] )
        assert_equal(compress_rowcols(x,1), [[1,2],[4,5],[7,8]] )
        x = array(x._data, mask=[[0,0,0],[0,1,0],[0,0,0]])
        assert_equal(compress_rowcols(x), [[0,2],[6,8]] )
        assert_equal(compress_rowcols(x,0), [[0,1,2],[6,7,8]] )
        assert_equal(compress_rowcols(x,1), [[0,2],[3,5],[6,8]] )
        x = array(x._data, mask=[[1,0,0],[0,1,0],[0,0,0]])
        assert_equal(compress_rowcols(x), [[8]] )
        assert_equal(compress_rowcols(x,0), [[6,7,8]] )
        assert_equal(compress_rowcols(x,1,), [[2],[5],[8]] )
        x = array(x._data, mask=[[1,0,0],[0,1,0],[0,0,1]])
        assert_equal(compress_rowcols(x).size, 0 )
        assert_equal(compress_rowcols(x,0).size, 0 )
        assert_equal(compress_rowcols(x,1).size, 0 )
    #
    def test_mask_rowcols(self):
        "Tests mask_rowcols."
        x = array(np.arange(9).reshape(3,3), mask=[[1,0,0],[0,0,0],[0,0,0]])
        assert_equal(mask_rowcols(x).mask, [[1,1,1],[1,0,0],[1,0,0]] )
        assert_equal(mask_rowcols(x,0).mask, [[1,1,1],[0,0,0],[0,0,0]] )
        assert_equal(mask_rowcols(x,1).mask, [[1,0,0],[1,0,0],[1,0,0]] )
        x = array(x._data, mask=[[0,0,0],[0,1,0],[0,0,0]])
        assert_equal(mask_rowcols(x).mask, [[0,1,0],[1,1,1],[0,1,0]] )
        assert_equal(mask_rowcols(x,0).mask, [[0,0,0],[1,1,1],[0,0,0]] )
        assert_equal(mask_rowcols(x,1).mask, [[0,1,0],[0,1,0],[0,1,0]] )
        x = array(x._data, mask=[[1,0,0],[0,1,0],[0,0,0]])
        assert_equal(mask_rowcols(x).mask, [[1,1,1],[1,1,1],[1,1,0]] )
        assert_equal(mask_rowcols(x,0).mask, [[1,1,1],[1,1,1],[0,0,0]] )
        assert_equal(mask_rowcols(x,1,).mask, [[1,1,0],[1,1,0],[1,1,0]] )
        x = array(x._data, mask=[[1,0,0],[0,1,0],[0,0,1]])
        self.failUnless(mask_rowcols(x).all() is masked)
        self.failUnless(mask_rowcols(x,0).all() is masked)
        self.failUnless(mask_rowcols(x,1).all() is masked)
        self.failUnless(mask_rowcols(x).mask.all())
        self.failUnless(mask_rowcols(x,0).mask.all())
        self.failUnless(mask_rowcols(x,1).mask.all())
    #
    def test_dot(self):
        "Tests dot product"
        n = np.arange(1,7)
        #
        m = [1,0,0,0,0,0]
        a = masked_array(n, mask=m).reshape(2,3)
        b = masked_array(n, mask=m).reshape(3,2)
        c = dot(a,b,True)
        assert_equal(c.mask, [[1,1],[1,0]])
        c = dot(b,a,True)
        assert_equal(c.mask, [[1,1,1],[1,0,0],[1,0,0]])
        c = dot(a,b,False)
        assert_equal(c, np.dot(a.filled(0), b.filled(0)))
        c = dot(b,a,False)
        assert_equal(c, np.dot(b.filled(0), a.filled(0)))
        #
        m = [0,0,0,0,0,1]
        a = masked_array(n, mask=m).reshape(2,3)
        b = masked_array(n, mask=m).reshape(3,2)
        c = dot(a,b,True)
        assert_equal(c.mask,[[0,1],[1,1]])
        c = dot(b,a,True)
        assert_equal(c.mask, [[0,0,1],[0,0,1],[1,1,1]])
        c = dot(a,b,False)
        assert_equal(c, np.dot(a.filled(0), b.filled(0)))
        assert_equal(c, dot(a,b))
        c = dot(b,a,False)
        assert_equal(c, np.dot(b.filled(0), a.filled(0)))
        #
        m = [0,0,0,0,0,0]
        a = masked_array(n, mask=m).reshape(2,3)
        b = masked_array(n, mask=m).reshape(3,2)
        c = dot(a,b)
        assert_equal(c.mask,nomask)
        c = dot(b,a)
        assert_equal(c.mask,nomask)
        #
        a = masked_array(n, mask=[1,0,0,0,0,0]).reshape(2,3)
        b = masked_array(n, mask=[0,0,0,0,0,0]).reshape(3,2)
        c = dot(a,b,True)
        assert_equal(c.mask,[[1,1],[0,0]])
        c = dot(a,b,False)
        assert_equal(c, np.dot(a.filled(0),b.filled(0)))
        c = dot(b,a,True)
        assert_equal(c.mask,[[1,0,0],[1,0,0],[1,0,0]])
        c = dot(b,a,False)
        assert_equal(c, np.dot(b.filled(0),a.filled(0)))
        #
        a = masked_array(n, mask=[0,0,0,0,0,1]).reshape(2,3)
        b = masked_array(n, mask=[0,0,0,0,0,0]).reshape(3,2)
        c = dot(a,b,True)
        assert_equal(c.mask,[[0,0],[1,1]])
        c = dot(a,b)
        assert_equal(c, np.dot(a.filled(0),b.filled(0)))
        c = dot(b,a,True)
        assert_equal(c.mask,[[0,0,1],[0,0,1],[0,0,1]])
        c = dot(b,a,False)
        assert_equal(c, np.dot(b.filled(0), a.filled(0)))
        #
        a = masked_array(n, mask=[0,0,0,0,0,1]).reshape(2,3)
        b = masked_array(n, mask=[0,0,1,0,0,0]).reshape(3,2)
        c = dot(a,b,True)
        assert_equal(c.mask,[[1,0],[1,1]])
        c = dot(a,b,False)
        assert_equal(c, np.dot(a.filled(0),b.filled(0)))
        c = dot(b,a,True)
        assert_equal(c.mask,[[0,0,1],[1,1,1],[0,0,1]])
        c = dot(b,a,False)
        assert_equal(c, np.dot(b.filled(0),a.filled(0)))



class TestApplyAlongAxis(TestCase):
    #
    "Tests 2D functions"
    def test_3d(self):
        a = arange(12.).reshape(2,2,3)
        def myfunc(b):
            return b[1]
        xa = apply_along_axis(myfunc,2,a)
        assert_equal(xa,[[1,4],[7,10]])



class TestMedian(TestCase):
    #
    def test_2d(self):
        "Tests median w/ 2D"
        (n,p) = (101,30)
        x = masked_array(np.linspace(-1.,1.,n),)
        x[:10] = x[-10:] = masked
        z = masked_array(np.empty((n,p), dtype=float))
        z[:,0] = x[:]
        idx = np.arange(len(x))
        for i in range(1,p):
            np.random.shuffle(idx)
            z[:,i] = x[idx]
        assert_equal(median(z[:,0]), 0)
        assert_equal(median(z), 0)
        assert_equal(median(z, axis=0), np.zeros(p))
        assert_equal(median(z.T, axis=1), np.zeros(p))
    #
    def test_2d_waxis(self):
        "Tests median w/ 2D arrays and different axis."
        x = masked_array(np.arange(30).reshape(10,3))
        x[:3] = x[-3:] = masked
        assert_equal(median(x), 14.5)
        assert_equal(median(x, axis=0), [13.5,14.5,15.5])
        assert_equal(median(x,axis=1), [0,0,0,10,13,16,19,0,0,0])
        assert_equal(median(x,axis=1).mask, [1,1,1,0,0,0,0,1,1,1])
    #
    def test_3d(self):
        "Tests median w/ 3D"
        x = np.ma.arange(24).reshape(3,4,2)
        x[x%3==0] = masked
        assert_equal(median(x,0), [[12,9],[6,15],[12,9],[18,15]])
        x.shape = (4,3,2)
        assert_equal(median(x,0),[[99,10],[11,99],[13,14]])
        x = np.ma.arange(24).reshape(4,3,2)
        x[x%5==0] = masked
        assert_equal(median(x,0), [[12,10],[8,9],[16,17]])



class TestCov(TestCase):

    def setUp(self):
        self.data = array(np.random.rand(12))

    def test_1d_wo_missing(self):
        "Test cov on 1D variable w/o missing values"
        x = self.data
        assert_almost_equal(np.cov(x), cov(x))
        assert_almost_equal(np.cov(x, rowvar=False), cov(x, rowvar=False))
        assert_almost_equal(np.cov(x, rowvar=False, bias=True),
                            cov(x, rowvar=False, bias=True))

    def test_2d_wo_missing(self):
        "Test cov on 1 2D variable w/o missing values"
        x = self.data.reshape(3,4)
        assert_almost_equal(np.cov(x), cov(x))
        assert_almost_equal(np.cov(x, rowvar=False), cov(x, rowvar=False))
        assert_almost_equal(np.cov(x, rowvar=False, bias=True),
                            cov(x, rowvar=False, bias=True))

    def test_1d_w_missing(self):
        "Test cov 1 1D variable w/missing values"
        x = self.data
        x[-1] = masked
        x -= x.mean()
        nx = x.compressed()
        assert_almost_equal(np.cov(nx), cov(x))
        assert_almost_equal(np.cov(nx, rowvar=False), cov(x, rowvar=False))
        assert_almost_equal(np.cov(nx, rowvar=False, bias=True),
                            cov(x, rowvar=False, bias=True))
        #
        try:
            cov(x, allow_masked=False)
        except ValueError:
            pass
        #
        # 2 1D variables w/ missing values
        nx = x[1:-1]
        assert_almost_equal(np.cov(nx, nx[::-1]), cov(x, x[::-1]))
        assert_almost_equal(np.cov(nx, nx[::-1], rowvar=False),
                            cov(x, x[::-1], rowvar=False))
        assert_almost_equal(np.cov(nx, nx[::-1], rowvar=False, bias=True),
                            cov(x, x[::-1], rowvar=False, bias=True))

    def test_2d_w_missing(self):
        "Test cov on 2D variable w/ missing value"
        x = self.data
        x[-1] = masked
        x = x.reshape(3,4)
        valid = np.logical_not(getmaskarray(x)).astype(int)
        frac = np.dot(valid, valid.T)
        xf = (x - x.mean(1)[:,None]).filled(0)
        assert_almost_equal(cov(x), np.cov(xf) * (x.shape[1]-1) / (frac - 1.))
        assert_almost_equal(cov(x, bias=True),
                            np.cov(xf, bias=True) * x.shape[1] / frac)
        frac = np.dot(valid.T, valid)
        xf = (x - x.mean(0)).filled(0)
        assert_almost_equal(cov(x, rowvar=False),
                            np.cov(xf, rowvar=False) * (x.shape[0]-1)/(frac - 1.))
        assert_almost_equal(cov(x, rowvar=False, bias=True),
                            np.cov(xf, rowvar=False, bias=True) * x.shape[0]/frac)



class TestCorrcoef(TestCase):

    def setUp(self):
        self.data = array(np.random.rand(12))

    def test_1d_wo_missing(self):
        "Test cov on 1D variable w/o missing values"
        x = self.data
        assert_almost_equal(np.corrcoef(x), corrcoef(x))
        assert_almost_equal(np.corrcoef(x, rowvar=False),
                            corrcoef(x, rowvar=False))
        assert_almost_equal(np.corrcoef(x, rowvar=False, bias=True),
                            corrcoef(x, rowvar=False, bias=True))

    def test_2d_wo_missing(self):
        "Test corrcoef on 1 2D variable w/o missing values"
        x = self.data.reshape(3,4)
        assert_almost_equal(np.corrcoef(x), corrcoef(x))
        assert_almost_equal(np.corrcoef(x, rowvar=False),
                            corrcoef(x, rowvar=False))
        assert_almost_equal(np.corrcoef(x, rowvar=False, bias=True),
                            corrcoef(x, rowvar=False, bias=True))

    def test_1d_w_missing(self):
        "Test corrcoef 1 1D variable w/missing values"
        x = self.data
        x[-1] = masked
        x -= x.mean()
        nx = x.compressed()
        assert_almost_equal(np.corrcoef(nx), corrcoef(x))
        assert_almost_equal(np.corrcoef(nx, rowvar=False), corrcoef(x, rowvar=False))
        assert_almost_equal(np.corrcoef(nx, rowvar=False, bias=True),
                            corrcoef(x, rowvar=False, bias=True))
        #
        try:
            corrcoef(x, allow_masked=False)
        except ValueError:
            pass
        #
        # 2 1D variables w/ missing values
        nx = x[1:-1]
        assert_almost_equal(np.corrcoef(nx, nx[::-1]), corrcoef(x, x[::-1]))
        assert_almost_equal(np.corrcoef(nx, nx[::-1], rowvar=False),
                            corrcoef(x, x[::-1], rowvar=False))
        assert_almost_equal(np.corrcoef(nx, nx[::-1], rowvar=False, bias=True),
                            corrcoef(x, x[::-1], rowvar=False, bias=True))

    def test_2d_w_missing(self):
        "Test corrcoef on 2D variable w/ missing value"
        x = self.data
        x[-1] = masked
        x = x.reshape(3,4)

        test = corrcoef(x)
        control = np.corrcoef(x)
        assert_almost_equal(test[:-1,:-1], control[:-1,:-1])



class TestPolynomial(TestCase):
    #
    def test_polyfit(self):
        "Tests polyfit"
        # On ndarrays
        x = np.random.rand(10)
        y = np.random.rand(20).reshape(-1,2)
        assert_almost_equal(polyfit(x,y,3),np.polyfit(x,y,3))
        # ON 1D maskedarrays
        x = x.view(MaskedArray)
        x[0] = masked
        y = y.view(MaskedArray)
        y[0,0] = y[-1,-1] = masked
        #
        (C,R,K,S,D) = polyfit(x,y[:,0],3,full=True)
        (c,r,k,s,d) = np.polyfit(x[1:], y[1:,0].compressed(), 3, full=True)
        for (a,a_) in zip((C,R,K,S,D),(c,r,k,s,d)):
            assert_almost_equal(a, a_)
        #
        (C,R,K,S,D) = polyfit(x,y[:,-1],3,full=True)
        (c,r,k,s,d) = np.polyfit(x[1:-1], y[1:-1,-1], 3, full=True)
        for (a,a_) in zip((C,R,K,S,D),(c,r,k,s,d)):
            assert_almost_equal(a, a_)
        #
        (C,R,K,S,D) = polyfit(x,y,3,full=True)
        (c,r,k,s,d) = np.polyfit(x[1:-1], y[1:-1,:], 3, full=True)
        for (a,a_) in zip((C,R,K,S,D),(c,r,k,s,d)):
            assert_almost_equal(a, a_)



class TestArraySetOps(TestCase):
    #
    def test_unique1d_onlist(self):
        "Test unique1d on list"
        data = [1, 1, 1, 2, 2, 3]
        test = unique1d(data, return_index=True, return_inverse=True)
        self.failUnless(isinstance(test[0], MaskedArray))
        assert_equal(test[0], masked_array([1, 2, 3], mask=[0, 0, 0]))
        assert_equal(test[1], [0, 3, 5])
        assert_equal(test[2], [0, 0, 0, 1, 1, 2])

    def test_unique1d_onmaskedarray(self):
        "Test unique1d on masked data w/use_mask=True"
        data = masked_array([1, 1, 1, 2, 2, 3], mask=[0, 0, 1, 0, 1, 0])
        test = unique1d(data, return_index=True, return_inverse=True)
        assert_equal(test[0], masked_array([1, 2, 3, -1], mask=[0, 0, 0, 1]))
        assert_equal(test[1], [0, 3, 5, 2])
        assert_equal(test[2], [0, 0, 3, 1, 3, 2])
        #
        data.fill_value = 3
        data = masked_array([1, 1, 1, 2, 2, 3],
                       mask=[0, 0, 1, 0, 1, 0], fill_value=3)
        test = unique1d(data, return_index=True, return_inverse=True)
        assert_equal(test[0], masked_array([1, 2, 3, -1], mask=[0, 0, 0, 1]))
        assert_equal(test[1], [0, 3, 5, 2])
        assert_equal(test[2], [0, 0, 3, 1, 3, 2])

    def test_unique1d_allmasked(self):
        "Test all masked"
        data = masked_array([1, 1, 1], mask=True)
        test = unique1d(data, return_index=True, return_inverse=True)
        assert_equal(test[0], masked_array([1,], mask=[True]))
        assert_equal(test[1], [0])
        assert_equal(test[2], [0, 0, 0])
        #
        "Test masked"
        data = masked
        test = unique1d(data, return_index=True, return_inverse=True)
        assert_equal(test[0], masked_array(masked))
        assert_equal(test[1], [0])
        assert_equal(test[2], [0])

    def test_ediff1d(self):
        "Tests mediff1d"
        x = masked_array(np.arange(5), mask=[1,0,0,0,1])
        control = array([1, 1, 1, 4], mask=[1, 0, 0, 1])
        test = ediff1d(x)
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
    #
    def test_ediff1d_tobegin(self):
        "Test ediff1d w/ to_begin"
        x = masked_array(np.arange(5), mask=[1,0,0,0,1])
        test = ediff1d(x, to_begin=masked)
        control = array([0, 1, 1, 1, 4], mask=[1, 1, 0, 0, 1])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
        #
        test = ediff1d(x, to_begin=[1,2,3])
        control = array([1, 2, 3, 1, 1, 1, 4], mask=[0, 0, 0, 1, 0, 0, 1])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
    #
    def test_ediff1d_toend(self):
        "Test ediff1d w/ to_end"
        x = masked_array(np.arange(5), mask=[1,0,0,0,1])
        test = ediff1d(x, to_end=masked)
        control = array([1, 1, 1, 4, 0], mask=[1, 0, 0, 1, 1])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
        #
        test = ediff1d(x, to_end=[1,2,3])
        control = array([1, 1, 1, 4, 1, 2, 3], mask=[1, 0, 0, 1, 0, 0, 0])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
    #
    def test_ediff1d_tobegin_toend(self):
        "Test ediff1d w/ to_begin and to_end"
        x = masked_array(np.arange(5), mask=[1,0,0,0,1])
        test = ediff1d(x, to_end=masked, to_begin=masked)
        control = array([0, 1, 1, 1, 4, 0], mask=[1, 1, 0, 0, 1, 1])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
        #
        test = ediff1d(x, to_end=[1,2,3], to_begin=masked)
        control = array([0, 1, 1, 1, 4, 1, 2, 3], mask=[1, 1, 0, 0, 1, 0, 0, 0])
        assert_equal(test, control)
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
    #
    def test_ediff1d_ndarray(self):
        "Test ediff1d w/ a ndarray"
        x = np.arange(5)
        test = ediff1d(x)
        control = array([1, 1, 1, 1], mask=[0, 0, 0, 0])
        assert_equal(test, control)
        self.failUnless(isinstance(test, MaskedArray))
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)
        #
        test = ediff1d(x, to_end=masked, to_begin=masked)
        control = array([0, 1, 1, 1, 1, 0], mask=[1, 0, 0, 0, 0, 1])
        self.failUnless(isinstance(test, MaskedArray))
        assert_equal(test.data, control.data)
        assert_equal(test.mask, control.mask)


    def test_intersect1d(self):
        "Test intersect1d"
        x = array([1, 3, 3, 3], mask=[0, 0, 0, 1])
        y = array([3, 1, 1, 1], mask=[0, 0, 0, 1])
        test = intersect1d(x, y)
        control = array([1, 1, 3, 3, -1], mask=[0, 0, 0, 0, 1])
        assert_equal(test, control)


    def test_intersect1d_nu(self):
        "Test intersect1d_nu"
        x = array([1, 3, 3, 3], mask=[0, 0, 0, 1])
        y = array([3, 1, 1, 1], mask=[0, 0, 0, 1])
        test = intersect1d_nu(x, y)
        control = array([1, 3, -1], mask=[0, 0, 1])
        assert_equal(test, control)


    def test_setxor1d(self):
        "Test setxor1d"
        a = array([1, 2, 5, 7, -1], mask=[0, 0, 0, 0, 1])
        b = array([1, 2, 3, 4, 5, -1], mask=[0, 0, 0, 0, 0, -1])
        test = setxor1d(a, b)
        assert_equal(test, array([3, 4, 7]))
        #
        a = array([1, 2, 5, 7, -1], mask=[0, 0, 0, 0, 1])
        b = [1, 2, 3, 4, 5]
        test = setxor1d(a, b)
        assert_equal(test, array([3, 4, 7, -1], mask=[0, 0, 0, 1]))
        #
        a = array( [1, 2, 3] )
        b = array( [6, 5, 4] )
        test = setxor1d(a, b)
        assert(isinstance(test, MaskedArray))
        assert_equal(test, [1, 2, 3, 4, 5, 6])
        #
        a = array([1, 8, 2, 3], mask=[0, 1, 0, 0])
        b = array([6, 5, 4, 8], mask=[0, 0, 0, 1])
        test = setxor1d(a, b)
        assert(isinstance(test, MaskedArray))
        assert_equal(test, [1, 2, 3, 4, 5, 6])
        #
        assert_array_equal([], setxor1d([],[]))


    def test_setmember1d( self ):
        "Test setmember1d"
        a = array([1, 2, 5, 7, -1], mask=[0, 0, 0, 0, 1])
        b = array([1, 2, 3, 4, 5, -1], mask=[0, 0, 0, 0, 0, -1])
        test = setmember1d(a, b)
        assert_equal(test, [True, True, True, False, True])
        #
        assert_array_equal([], setmember1d([],[]))


    def test_union1d( self ):
        "Test union1d"
        a = array([1, 2, 5, 7, -1], mask=[0, 0, 0, 0, 1])
        b = array([1, 2, 3, 4, 5, -1], mask=[0, 0, 0, 0, 0, -1])
        test = union1d(a, b)
        control = array([1, 2, 3, 4, 5, 7, -1], mask=[0, 0, 0, 0, 0, 0, 1])
        assert_equal(test, control)
        #
        assert_array_equal([], setmember1d([],[]))


    def test_setdiff1d( self ):
        "Test setdiff1d"
        a = array([6, 5, 4, 7, 1, 2, 1], mask=[0, 0, 0, 0, 0, 0, 1])
        b = array([2, 4, 3, 3, 2, 1, 5])
        test = setdiff1d(a, b)
        assert_equal(test, array([6, 7, -1], mask=[0, 0, 1]))
        #
        a = arange(10)
        b = arange(8)
        assert_equal(setdiff1d(a, b), array([8, 9]))


    def test_setdiff1d_char_array(self):
        "Test setdiff1d_charray"
        a = np.array(['a','b','c'])
        b = np.array(['a','b','s'])
        assert_array_equal(setdiff1d(a,b), np.array(['c']))




class TestShapeBase(TestCase):
    #
    def test_atleast1d(self):
        pass


###############################################################################
#------------------------------------------------------------------------------
if __name__ == "__main__":
    run_module_suite()
